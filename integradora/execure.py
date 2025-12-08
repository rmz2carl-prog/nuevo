import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from skyable import SkyAble
from usuario import Paciente, Especialista, Admin, hash_password

skyable = SkyAble()
current_user = None

def login_inicial():
    global current_user

    tiene = messagebox.askyesno("Bienvenido a SkyAble", "¿Tienes una cuenta en el sistema?")
    if not tiene:
        try:
            u = registrar_usuario_publico()
            if u:
                current_user = u
                user_name = u.ad_nom if hasattr(u, 'ad_nom') else u.es_nombre if hasattr(u, 'es_nombre') else u.pa_nombre
                lbl_help.config(text=f"Usuario conectado: {user_name} ({type(u).__name__})")
                ajustar_menu_por_rol()
                listar_pacientes()
                return
            else:
                messagebox.showinfo("Info", "Registro cancelado")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el registro:\n{e}")

    for _ in range(3):
        login = simpledialog.askstring("Inicio de sesion", "Correo electronico:")
        if login is None:
            salir()
            return
        pwd = simpledialog.askstring("Inicio de sesion", "Contraseña:", show='*')
        if pwd is None:
            salir()
            return
        
        usuario = None
        usuario = Admin.autenticar(login.strip(), pwd)
        if not usuario:
            usuario = Especialista.autenticar(login.strip(), pwd)
        if not usuario:
            usuario = Paciente.autenticar(login.strip(), pwd)
            
        if usuario:
            current_user = usuario
            user_name = usuario.ad_nom if hasattr(usuario, 'ad_nom') else usuario.es_nombre if hasattr(usuario, 'es_nombre') else usuario.pa_nombre
            lbl_help.config(text=f"Usuario conectado: {user_name} ({type(usuario).__name__})")
            ajustar_menu_por_rol()
            listar_pacientes()
            return
        else:
            retry = messagebox.askretrycancel("Error", "Credenciales incorrectas. ¿Deseas intentar de nuevo?")
            if not retry:
                want_reg = messagebox.askyesno("Registro", "¿Quieres registrarte ahora?")
                if want_reg:
                    try:
                        u = registrar_usuario_publico()
                        if u:
                            current_user = u
                            user_name = u.ad_nom if hasattr(u, 'ad_nom') else u.es_nombre if hasattr(u, 'es_nombre') else u.pa_nombre
                            lbl_help.config(text=f"Usuario conectado: {user_name} ({type(u).__name__})")
                            ajustar_menu_por_rol()
                            listar_pacientes()
                            return
                    except Exception as e:
                        messagebox.showerror("Error", f"Error durante el registro:\n{e}")
    messagebox.showerror("Error", "Demasiados intentos fallidos. Saliendo.")
    salir()

def requiere_admin(func):
    def wrapper(*args, **kwargs):
        if current_user is None or not hasattr(current_user, 'ad_clave'):
            messagebox.showerror("Permisos", "Accion restringida: se requiere usuario Admin.")
            return
        return func(*args, **kwargs)
    return wrapper

def requiere_especialista(func):
    def wrapper(*args, **kwargs):
        if current_user is None or (not hasattr(current_user, 'es_clave') and not hasattr(current_user, 'ad_clave')):
            messagebox.showerror("Permisos", "Accion restringida: se requiere Especialista o Admin.")
            return
        return func(*args, **kwargs)
    return wrapper

def registrar_usuario_publico():
    tipo = simpledialog.askstring("Registrar usuario", "Tipo (admin/especialista/paciente):", initialvalue="paciente")
    if not tipo:
        return None
    tipo = tipo.strip().lower()
    
    nombre = simpledialog.askstring("Registrar usuario", "Nombre:")
    if not nombre:
        return None
    correo = simpledialog.askstring("Registrar usuario", "Correo electrónico:")
    if not correo:
        return None
    pwd = simpledialog.askstring("Registrar usuario", "Contraseña:", show='*')
    if not pwd:
        return None

    try:
        if tipo == 'admin':
            u = Admin.crear(nombre.strip(), correo.strip(), pwd)
        elif tipo == 'especialista':
            admins = Admin.listar_todos()
            if not admins:
                messagebox.showerror("Error", "No hay administradores en el sistema. Debe registrar un administrador primero.")
                return None
            admin_id = admins[0].ad_clave
            u = Especialista.crear(nombre.strip(), correo.strip(), pwd, 'no', admin_id)
        else:
            especialistas = Especialista.listar_todos()
            if not especialistas:
                messagebox.showerror("Error", "No hay especialistas en el sistema. Debe registrar un especialista primero.")
                return None
            discapacidad = simpledialog.askstring("Registrar paciente", "Tipo de discapacidad:")
            if not discapacidad:
                return None
            fnac = simpledialog.askstring("Registrar paciente", "Fecha nacimiento (YYYY-MM-DD):")
            if not fnac:
                return None
            sesiones = simpledialog.askinteger("Registrar paciente", "Sesiones por semana (1-7):", minvalue=1, maxvalue=7)
            if not sesiones:
                return None
            especialista_id = especialistas[0].es_clave
            u = Paciente.crear(nombre.strip(), discapacidad.strip(), fnac.strip(), correo.strip(), pwd, sesiones, especialista_id)
        
        messagebox.showinfo("OK", f"Usuario registrado: {nombre} ({tipo})")
        return u
    except Exception as e:
        messagebox.showerror("Error", f"Error al registrar usuario:\n{e}")
        return None

@requiere_admin
def registrar_especialista():
    nombre = simpledialog.askstring("Registrar especialista", "Nombre del especialista:")
    if not nombre:
        return
    correo = simpledialog.askstring("Registrar especialista", "Correo del especialista:")
    if not correo:
        return
    pwd = simpledialog.askstring("Registrar especialista", "Contraseña:", show='*')
    if not pwd:
        return
    padesig = simpledialog.askstring("Registrar especialista", "Pacientes designados (si/no):", initialvalue="no")
    
    try:
        u = skyable.registrar_especialista(nombre.strip(), correo.strip(), pwd, padesig.strip(), current_user.ad_clave)
        messagebox.showinfo("OK", f"Especialista registrado: {u.es_nombre} (id={u.es_clave})")
        listar_especialistas()
    except Exception as e:
        messagebox.showerror("Error", f"Error al registrar especialista:\n{e}")

@requiere_admin
def modificar_especialista():
    correo = simpledialog.askstring("Modificar especialista", "Correo del especialista a modificar:")
    if not correo:
        return
    esp = skyable.buscar_especialista(correo.strip())
    if esp is None:
        messagebox.showwarning("No encontrado", "Especialista no encontrado.")
        return
    nuevo_nombre = simpledialog.askstring("Modificar especialista", "Nuevo nombre:", initialvalue=esp.es_nombre)
    nuevo_correo = simpledialog.askstring("Modificar especialista", "Nuevo correo:", initialvalue=esp.es_correo)
    nuevo_padesig = simpledialog.askstring("Modificar especialista", "Pacientes designados (si/no):", initialvalue=esp.es_padesig)
    
    try:
        conn = __import__('db_connection').get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE especialista SET es_nombre=%s, es_correo=%s, es_padesig=%s WHERE es_clave=%s",
                    (nuevo_nombre.strip(), nuevo_correo.strip(), nuevo_padesig.strip(), esp.es_clave))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("OK", "Especialista modificado.")
        listar_especialistas()
    except Exception as e:
        messagebox.showerror("Error", f"Error al modificar especialista:\n{e}")

@requiere_admin
def eliminar_especialista():
    correo = simpledialog.askstring("Eliminar especialista", "Correo del especialista a eliminar:")
    if not correo:
        return
    esp = skyable.buscar_especialista(correo.strip())
    if esp is None:
        messagebox.showwarning("No encontrado", "Especialista no encontrado.")
        return
    if messagebox.askyesno("Confirmar", f"¿Eliminar al especialista '{esp.es_nombre}' (id={esp.es_clave})?"):
        try:
            success, message = skyable.eliminar_especialista_por_id(esp.es_clave)
            if success:
                messagebox.showinfo("OK", message)
            else:
                messagebox.showerror("Error", message)
            listar_especialistas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar especialista:\n{e}")

@requiere_especialista
def registrar_paciente():
    nombre = simpledialog.askstring("Registrar paciente", "Nombre del paciente:")
    if not nombre:
        return
    discapacidad = simpledialog.askstring("Registrar paciente", "Tipo de discapacidad:")
    if not discapacidad:
        return
    fnac = simpledialog.askstring("Registrar paciente", "Fecha nacimiento (YYYY-MM-DD):")
    if not fnac:
        return
    correo = simpledialog.askstring("Registrar paciente", "Correo del paciente:")
    if not correo:
        return
    pwd = simpledialog.askstring("Registrar paciente", "Contraseña:", show='*')
    if not pwd:
        return
    sesiones = simpledialog.askinteger("Registrar paciente", "Sesiones por semana 1-7:", minvalue=1, maxvalue=7)
    if not sesiones:
        return
    
    try:
        if hasattr(current_user, 'es_clave'):
            especialista_id = current_user.es_clave
        else:
            especialistas = Especialista.listar_todos()
            if not especialistas:
                messagebox.showerror("Error", "No hay especialistas disponibles.")
                return
            especialista_id = especialistas[0].es_clave
            
        u = skyable.registrar_paciente(nombre.strip(), discapacidad.strip(), fnac.strip(), correo.strip(), pwd, sesiones, especialista_id)
        messagebox.showinfo("OK", f"Paciente registrado: {u.pa_nombre} (id={u.pa_clave})")
        listar_pacientes()
    except Exception as e:
        messagebox.showerror("Error", f"Error al registrar paciente:\n{e}")

@requiere_especialista
def modificar_paciente():
    correo = simpledialog.askstring("Modificar paciente", "Correo del paciente a modificar:")
    if not correo:
        return
    pac = skyable.buscar_paciente(correo.strip())
    if pac is None:
        messagebox.showwarning("No encontrado", "Paciente no encontrado.")
        return
    nuevo_nombre = simpledialog.askstring("Modificar paciente", "Nuevo nombre:", initialvalue=pac.pa_nombre)
    nueva_discapacidad = simpledialog.askstring("Modificar paciente", "Nueva discapacidad:", initialvalue=pac.pa_tdiscapacidad)
    nuevo_correo = simpledialog.askstring("Modificar paciente", "Nuevo correo:", initialvalue=pac.pa_correo)
    nuevas_sesiones = simpledialog.askinteger("Modificar paciente", "Nuevas sesiones por semana:", initialvalue=pac.pa_sesemana, minvalue=1, maxvalue=7)
    
    try:
        conn = __import__('db_connection').get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE paciente SET pa_nombre=%s, pa_tdiscapacidad=%s, pa_correo=%s, pa_sesemana=%s WHERE pa_clave=%s",
                    (nuevo_nombre.strip(), nueva_discapacidad.strip(), nuevo_correo.strip(), nuevas_sesiones, pac.pa_clave))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("OK", "Paciente modificado.")
        listar_pacientes()
    except Exception as e:
        messagebox.showerror("Error", f"Error al modificar paciente:\n{e}")

@requiere_especialista
def eliminar_paciente():
    correo = simpledialog.askstring("Eliminar paciente", "Correo del paciente a eliminar:")
    if not correo:
        return
    pac = skyable.buscar_paciente(correo.strip())
    if pac is None:
        messagebox.showwarning("No encontrado", "Paciente no encontrado.")
        return
    if messagebox.askyesno("Confirmar", f"¿Eliminar al paciente '{pac.pa_nombre}' (id={pac.pa_clave})?"):
        try:
            success, message = skyable.eliminar_paciente_por_id(pac.pa_clave)
            if success:
                messagebox.showinfo("OK", message)
            else:
                messagebox.showerror("Error", message)
            listar_pacientes()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar paciente:\n{e}")

@requiere_admin
def registrar_producto():
    tipo = simpledialog.askstring("Registrar producto", "Tipo (sensores_brazos/sensores_piernas):")
    if not tipo:
        return
    precio = simpledialog.askfloat("Registrar producto", "Precio:")
    if not precio:
        return
    cantidad = simpledialog.askinteger("Registrar producto", "Cantidad en stock:", minvalue=0)
    if cantidad is None:
        return
    
    try:
        p = skyable.registrar_producto(tipo.strip(), precio, cantidad)
        messagebox.showinfo("OK", f"Producto registrado: {p.pr_tipo} (id={p.pr_clave})")
        listar_productos()
    except Exception as e:
        messagebox.showerror("Error", f"Error al registrar producto:\n{e}")

@requiere_admin
def modificar_producto():
    tipo = simpledialog.askstring("Modificar producto", "Tipo del producto a modificar:")
    if not tipo:
        return
    prod = skyable.buscar_producto(tipo.strip())
    if prod is None:
        messagebox.showwarning("No encontrado", "Producto no encontrado.")
        return
    nuevo_tipo = simpledialog.askstring("Modificar producto", "Nuevo tipo:", initialvalue=prod.pr_tipo)
    nuevo_precio = simpledialog.askfloat("Modificar producto", "Nuevo precio:", initialvalue=float(prod.pr_precio))
    nueva_cantidad = simpledialog.askinteger("Modificar producto", "Nueva cantidad:", initialvalue=prod.pr_cantidad, minvalue=0)
    
    try:
        conn = __import__('db_connection').get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE productos SET pr_tipo=%s, pr_precio=%s, pr_cantidad=%s WHERE pr_clave=%s", 
                    (nuevo_tipo.strip(), nuevo_precio, nueva_cantidad, prod.pr_clave))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("OK", "Producto modificado.")
        listar_productos()
    except Exception as e:
        messagebox.showerror("Error", f"Error al modificar producto:\n{e}")

@requiere_admin
def eliminar_producto():
    tipo = simpledialog.askstring("Eliminar producto", "Tipo del producto a eliminar:")
    if not tipo:
        return
    prod = skyable.buscar_producto(tipo.strip())
    if prod is None:
        messagebox.showwarning("No encontrado", "Producto no encontrado.")
        return
    if messagebox.askyesno("Confirmar", f"¿Eliminar el producto '{prod.pr_tipo}' (id={prod.pr_clave})?"):
        try:
            success, message = skyable.eliminar_producto_por_id(prod.pr_clave)
            if success:
                messagebox.showinfo("OK", message)
            else:
                messagebox.showerror("Error", message)
            listar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar producto:\n{e}")

def vender_producto():
    """Vender producto a paciente"""
    if current_user is None:
        messagebox.showerror("Permisos", "Debe iniciar sesión.")
        return
    
    producto_id = simpledialog.askinteger("Vender producto", "ID del producto:")
    if not producto_id:
        return
        
    paciente_correo = simpledialog.askstring("Vender producto", "Correo del paciente:")
    if not paciente_correo:
        return
        
    cantidad = simpledialog.askinteger("Vender producto", "Cantidad:", minvalue=1)
    if not cantidad:
        return
        
    try:
        paciente = skyable.buscar_paciente(paciente_correo.strip())
        if paciente is None:
            messagebox.showwarning("No encontrado", "Paciente no encontrado.")
            return
            
        msg = skyable.vender_producto(producto_id, paciente.pa_clave, cantidad)
        messagebox.showinfo("Resultado", msg)
        listar_productos()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al vender producto:\n{e}")

def listar_ventas():
    """Listar todas las ventas realizadas"""
    try:
        conn = __import__('db_connection').get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT v.ve_clave, v.ve_fecha, p.pa_nombre, pr.pr_tipo, v.ve_cantidad, v.ve_total 
            FROM ventas v
            JOIN paciente p ON v.pa_clave = p.pa_clave
            JOIN productos pr ON v.pr_clave = pr.pr_clave
            ORDER BY v.ve_fecha DESC
        """)
        rows = cur.fetchall()
        
        lb_output.delete(0, tk.END)
        if not rows:
            lb_output.insert(tk.END, "No hay ventas registradas.")
            return
            
        lb_output.insert(tk.END, "Ventas:")
        for r in rows:
            lb_output.insert(tk.END, f"  [{r[0]}] {r[1]} - {r[2]} - {r[3]} x{r[4]} - ${r[5]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar ventas:\n{e}")

def listar_pacientes():
    try:
        pacientes = skyable.listar_pacientes()
        lb_output.delete(0, tk.END)
        if not pacientes:
            lb_output.insert(tk.END, "No hay pacientes registrados.")
            return
        lb_output.insert(tk.END, "Pacientes:")
        for p in pacientes:
            lb_output.insert(tk.END, f"  [{p.pa_clave}] {p.pa_nombre} — {p.pa_tdiscapacidad} — {p.pa_sesemana} ses/sem")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar pacientes:\n{e}")

def listar_especialistas():
    try:
        especialistas = skyable.listar_especialistas()
        lb_output.delete(0, tk.END)
        if not especialistas:
            lb_output.insert(tk.END, "No hay especialistas registrados.")
            return
        lb_output.insert(tk.END, "Especialistas:")
        for e in especialistas:
            lb_output.insert(tk.END, f"  [{e.es_clave}] {e.es_nombre} — {e.es_correo} — Pacientes: {e.es_padesig}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar especialistas:\n{e}")

def listar_admins():
    try:
        admins = skyable.listar_admins()
        lb_output.delete(0, tk.END)
        if not admins:
            lb_output.insert(tk.END, "No hay administradores registrados.")
            return
        lb_output.insert(tk.END, "Administradores:")
        for a in admins:
            lb_output.insert(tk.END, f"  [{a.ad_clave}] {a.ad_nom} — {a.ad_correo}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar administradores:\n{e}")

def listar_productos():
    try:
        productos = skyable.listar_productos()
        lb_output.delete(0, tk.END)
        if not productos:
            lb_output.insert(tk.END, "No hay productos registrados.")
            return
        lb_output.insert(tk.END, "Productos:")
        for p in productos:
            lb_output.insert(tk.END, f"  [{p.pr_clave}] {p.pr_tipo} — ${p.pr_precio} — Stock: {p.pr_cantidad}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar productos:\n{e}")

def listar_terapias():
    try:
        terapias = skyable.listar_terapias()
        lb_output.delete(0, tk.END)
        if not terapias:
            lb_output.insert(tk.END, "No hay terapias registradas.")
            return
        lb_output.insert(tk.END, "Terapias:")
        for t in terapias:
            lb_output.insert(tk.END, f"  [{t.te_clave}] Inicio: {t.te_finicio} — Sesiones: {t.te_sescom}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar terapias:\n{e}")

def salir():
    root.destroy()
    sys.exit(0)

def ajustar_menu_por_rol():
    if current_user is None:
        acciones_menu.entryconfig("Registrar especialista", state="disabled")
        acciones_menu.entryconfig("Modificar especialista", state="disabled")
        acciones_menu.entryconfig("Eliminar especialista", state="disabled")
        acciones_menu.entryconfig("Registrar paciente", state="disabled")
        acciones_menu.entryconfig("Modificar paciente", state="disabled")
        acciones_menu.entryconfig("Eliminar paciente", state="disabled")
        acciones_menu.entryconfig("Registrar producto", state="disabled")
        acciones_menu.entryconfig("Modificar producto", state="disabled")
        acciones_menu.entryconfig("Eliminar producto", state="disabled")
        acciones_menu.entryconfig("Vender producto", state="disabled")
        acciones_menu.entryconfig("Mostrar ventas", state="disabled")
        acciones_menu.entryconfig("Mostrar pacientes", state="disabled")
        acciones_menu.entryconfig("Mostrar especialistas", state="disabled")
        acciones_menu.entryconfig("Mostrar administradores", state="disabled")
        acciones_menu.entryconfig("Mostrar productos", state="disabled")
        acciones_menu.entryconfig("Mostrar terapias", state="disabled")
        return

    if hasattr(current_user, 'ad_clave'):
        acciones_menu.entryconfig("Registrar especialista", state="normal")
        acciones_menu.entryconfig("Modificar especialista", state="normal")
        acciones_menu.entryconfig("Eliminar especialista", state="normal")
        acciones_menu.entryconfig("Registrar paciente", state="normal")
        acciones_menu.entryconfig("Modificar paciente", state="normal")
        acciones_menu.entryconfig("Eliminar paciente", state="normal")
        acciones_menu.entryconfig("Registrar producto", state="normal")
        acciones_menu.entryconfig("Modificar producto", state="normal")
        acciones_menu.entryconfig("Eliminar producto", state="normal")
        acciones_menu.entryconfig("Vender producto", state="normal")
        acciones_menu.entryconfig("Mostrar ventas", state="normal")
        acciones_menu.entryconfig("Mostrar pacientes", state="normal")
        acciones_menu.entryconfig("Mostrar especialistas", state="normal")
        acciones_menu.entryconfig("Mostrar administradores", state="normal")
        acciones_menu.entryconfig("Mostrar productos", state="normal")
        acciones_menu.entryconfig("Mostrar terapias", state="normal")
    
    elif hasattr(current_user, 'es_clave'):
        acciones_menu.entryconfig("Registrar especialista", state="disabled")
        acciones_menu.entryconfig("Modificar especialista", state="disabled")
        acciones_menu.entryconfig("Eliminar especialista", state="disabled")
        acciones_menu.entryconfig("Registrar producto", state="disabled")
        acciones_menu.entryconfig("Modificar producto", state="disabled")
        acciones_menu.entryconfig("Eliminar producto", state="disabled")
        acciones_menu.entryconfig("Mostrar administradores", state="disabled")
        acciones_menu.entryconfig("Registrar paciente", state="normal")
        acciones_menu.entryconfig("Modificar paciente", state="normal")
        acciones_menu.entryconfig("Eliminar paciente", state="normal")
        acciones_menu.entryconfig("Vender producto", state="normal")
        acciones_menu.entryconfig("Mostrar ventas", state="normal")
        acciones_menu.entryconfig("Mostrar pacientes", state="normal")
        acciones_menu.entryconfig("Mostrar especialistas", state="normal")
        acciones_menu.entryconfig("Mostrar productos", state="normal")
        acciones_menu.entryconfig("Mostrar terapias", state="normal")
    
    else:
        acciones_menu.entryconfig("Registrar especialista", state="disabled")
        acciones_menu.entryconfig("Modificar especialista", state="disabled")
        acciones_menu.entryconfig("Eliminar especialista", state="disabled")
        acciones_menu.entryconfig("Registrar paciente", state="disabled")
        acciones_menu.entryconfig("Modificar paciente", state="disabled")
        acciones_menu.entryconfig("Eliminar paciente", state="disabled")
        acciones_menu.entryconfig("Registrar producto", state="disabled")
        acciones_menu.entryconfig("Modificar producto", state="disabled")
        acciones_menu.entryconfig("Eliminar producto", state="disabled")
        acciones_menu.entryconfig("Vender producto", state="disabled")
        acciones_menu.entryconfig("Mostrar administradores", state="disabled")
        acciones_menu.entryconfig("Mostrar pacientes", state="normal")
        acciones_menu.entryconfig("Mostrar especialistas", state="normal")
        acciones_menu.entryconfig("Mostrar productos", state="normal")
        acciones_menu.entryconfig("Mostrar terapias", state="normal")
        acciones_menu.entryconfig("Mostrar ventas", state="normal")

def create_tables():
    conn = __import__('db_connection').get_conn()
    queries = [
        """
        CREATE TABLE IF NOT EXISTS admin (
            ad_clave INT AUTO_INCREMENT PRIMARY KEY,
            ad_nom VARCHAR(100) NOT NULL,
            ad_correo VARCHAR(100) UNIQUE NOT NULL,
            ad_contraseña VARCHAR(255) NOT NULL,
            INDEX idx_admin_correo (ad_correo)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS especialista (
            es_clave INT AUTO_INCREMENT PRIMARY KEY,
            es_nombre VARCHAR(100) NOT NULL,
            es_correo VARCHAR(100) UNIQUE NOT NULL,
            es_contraseña VARCHAR(255) NOT NULL,
            es_padesig ENUM('si', 'no') DEFAULT 'no',
            ad_clave INT NOT NULL,
            FOREIGN KEY (ad_clave) REFERENCES admin(ad_clave) ON DELETE RESTRICT,
            INDEX idx_especialista_correo (es_correo),
            INDEX idx_especialista_admin (ad_clave)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS paciente (
            pa_clave INT AUTO_INCREMENT PRIMARY KEY,
            pa_nombre VARCHAR(100) NOT NULL,
            pa_tdiscapacidad VARCHAR(50) NOT NULL,
            pa_fnac DATE NOT NULL,
            pa_correo VARCHAR(100) UNIQUE NOT NULL,
            pa_contraseña VARCHAR(255) NOT NULL,
            pa_sesemana INT CHECK (pa_sesemana BETWEEN 1 AND 7),
            es_clave INT NOT NULL,
            FOREIGN KEY (es_clave) REFERENCES especialista(es_clave) ON DELETE RESTRICT,
            INDEX idx_paciente_correo (pa_correo),
            INDEX idx_paciente_especialista (es_clave)
        ) ENGINE=InnoDB;
        """,
       """
        CREATE TABLE IF NOT EXISTS productos (
            pr_clave INT AUTO_INCREMENT PRIMARY KEY,
            pr_tipo ENUM('sensores_brazos', 'sensores_piernas') NOT NULL unique,
            pr_precio DECIMAL(10,2) CHECK (pr_precio >= 0),
            pr_cantidad INT CHECK (pr_cantidad >= 0) DEFAULT 0,
            INDEX idx_productos_tipo (pr_tipo)
        ) ENGINE=InnoDB;
        """,
       
        """
        CREATE TABLE IF NOT EXISTS terapia (
            te_clave INT AUTO_INCREMENT PRIMARY KEY,
            te_finicio DATE NOT NULL,
            te_sescom INT CHECK (te_sescom >= 0) DEFAULT 0,
            pa_clave INT NOT NULL,
            es_clave INT NOT NULL,
            FOREIGN KEY (pa_clave) REFERENCES paciente(pa_clave) ON DELETE CASCADE,
            FOREIGN KEY (es_clave) REFERENCES especialista(es_clave) ON DELETE RESTRICT,
            INDEX idx_terapia_paciente (pa_clave),
            INDEX idx_terapia_especialista (es_clave)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS ventas (
            ve_clave INT AUTO_INCREMENT PRIMARY KEY,
            ve_fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ve_cantidad INT CHECK (ve_cantidad > 0),
            ve_total DECIMAL(10,2) CHECK (ve_total >= 0),
            pa_clave INT NOT NULL,
            pr_clave INT NOT NULL,
            FOREIGN KEY (pa_clave) REFERENCES paciente(pa_clave),
            FOREIGN KEY (pr_clave) REFERENCES productos(pr_clave)
        ) ENGINE=InnoDB;
        """
    ]
    
    cursor = conn.cursor()
    for query in queries:
        cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    print("Tablas creadas exitosamente.")

def main():
    global root, lbl_help, lb_output, acciones_menu
    
    print("Creando base de datos SkyAble...")
    create_tables()
    print("Base de datos configurada exitosamente.")
    print("Iniciando interfaz gráfica...")
    
    root = tk.Tk()
    root.title("SkyAble - Sistema de Terapias")
    root.geometry("800x480")
    root.minsize(700, 420)

    menubar = tk.Menu(root)

    acciones_menu = tk.Menu(menubar, tearoff=0)
    acciones_menu.add_command(label="Registrar especialista", command=registrar_especialista)
    acciones_menu.add_command(label="Modificar especialista", command=modificar_especialista)
    acciones_menu.add_command(label="Eliminar especialista", command=eliminar_especialista)
    acciones_menu.add_separator()
    acciones_menu.add_command(label="Registrar paciente", command=registrar_paciente)
    acciones_menu.add_command(label="Modificar paciente", command=modificar_paciente)
    acciones_menu.add_command(label="Eliminar paciente", command=eliminar_paciente)
    acciones_menu.add_separator()
    acciones_menu.add_command(label="Registrar producto", command=registrar_producto)
    acciones_menu.add_command(label="Modificar producto", command=modificar_producto)
    acciones_menu.add_command(label="Eliminar producto", command=eliminar_producto)
    acciones_menu.add_separator()
    acciones_menu.add_command(label="Vender producto", command=vender_producto)
    acciones_menu.add_command(label="Mostrar ventas", command=listar_ventas)
    acciones_menu.add_separator()
    acciones_menu.add_command(label="Mostrar pacientes", command=listar_pacientes)
    acciones_menu.add_command(label="Mostrar especialistas", command=listar_especialistas)
    acciones_menu.add_command(label="Mostrar administradores", command=listar_admins)
    acciones_menu.add_command(label="Mostrar productos", command=listar_productos)
    acciones_menu.add_command(label="Mostrar terapias", command=listar_terapias)
    menubar.add_cascade(label="Acciones", menu=acciones_menu)

    archivo_menu = tk.Menu(menubar, tearoff=0)
    archivo_menu.add_command(label="Salir", command=salir)
    menubar.add_cascade(label="Archivo", menu=archivo_menu)

    root.config(menu=menubar)

    frame_output = ttk.Frame(root, padding=(12, 12))
    frame_output.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    lbl_output = ttk.Label(frame_output, text="Salida", font=("Segoe UI", 12, "bold"))
    lbl_output.pack(anchor="w")

    frame_list = ttk.Frame(frame_output)
    frame_list.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

    sb = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
    lb_output = tk.Listbox(frame_list, yscrollcommand=sb.set, font=("Consolas", 10))
    sb.config(command=lb_output.yview)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    lb_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    lbl_help = ttk.Label(frame_output, text="Iniciando SkyAble...", font=("Segoe UI", 9))
    lbl_help.pack(anchor="w", pady=(8, 0))

    root.after(100, login_inicial)

    root.mainloop()

if __name__ == "__main__":
    main()