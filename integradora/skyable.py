from usuario import Paciente, Especialista, Admin
from productos import Productos, Terapia

class SkyAble:
    def __init__(self):
        pass

    def registrar_paciente(self, pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pa_contraseña, pa_sesemana, es_clave):
        return Paciente.crear(pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pa_contraseña, pa_sesemana, es_clave)

    def registrar_especialista(self, es_nombre, es_correo, es_contraseña, es_padesig, ad_clave):
        return Especialista.crear(es_nombre, es_correo, es_contraseña, es_padesig, ad_clave)

    def registrar_admin(self, ad_nom, ad_correo, ad_contraseña):
        return Admin.crear(ad_nom, ad_correo, ad_contraseña)

    def registrar_producto(self, pr_tipo, pr_precio, pr_cantidad):
        return Productos.crear(pr_tipo, pr_precio, pr_cantidad)

    def registrar_terapia(self, te_finicio, te_sescom, pa_clave, es_clave):
        return Terapia.crear(te_finicio, te_sescom, pa_clave, es_clave)

    def buscar_paciente(self, pa_correo):
        return Paciente.buscar_por_correo(pa_correo)

    def buscar_especialista(self, es_correo):
        return Especialista.buscar_por_correo(es_correo)

    def buscar_admin(self, ad_correo):
        return Admin.buscar_por_correo(ad_correo)

    def buscar_producto(self, pr_tipo):
        return Productos.buscar_por_tipo(pr_tipo)

    def buscar_producto_por_id(self, pr_clave):
        return Productos.buscar_por_id(pr_clave)

    def listar_pacientes(self):
        return Paciente.listar_todos()

    def listar_especialistas(self):
        return Especialista.listar_todos()

    def listar_admins(self):
        return Admin.listar_todos()

    def listar_productos(self):
        return Productos.listar_todos()

    def listar_terapias(self):
        return Terapia.listar_todos()

    def eliminar_paciente_por_id(self, pa_clave):
        try:
            conn = __import__('db_connection').get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM paciente WHERE pa_clave = %s", (pa_clave,))
            conn.commit()
            cur.close()
            conn.close()
            return True, "Paciente eliminado correctamente"
        except Exception as e:
            return False, f"Error al eliminar paciente: {e}"

    def eliminar_especialista_por_id(self, es_clave):
        try:
            conn = __import__('db_connection').get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM especialista WHERE es_clave = %s", (es_clave,))
            conn.commit()
            cur.close()
            conn.close()
            return True, "Especialista eliminado correctamente"
        except Exception as e:
            return False, f"Error al eliminar especialista: {e}"

    def eliminar_producto_por_id(self, pr_clave):
        try:
            conn = __import__('db_connection').get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM productos WHERE pr_clave = %s", (pr_clave,))
            conn.commit()
            cur.close()
            conn.close()
            return True, "Producto eliminado correctamente"
        except Exception as e:
            return False, f"Error al eliminar producto: {e}"

    def eliminar_terapia_por_id(self, te_clave):
        try:
            conn = __import__('db_connection').get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM terapia WHERE te_clave = %s", (te_clave,))
            conn.commit()
            cur.close()
            conn.close()
            return True, "Terapia eliminada correctamente"
        except Exception as e:
            return False, f"Error al eliminar terapia: {e}"

    def vender_producto(self, producto_id, paciente_id, cantidad):
        """Vende un producto a un paciente"""
        try:
            producto = self.buscar_producto_por_id(producto_id)
            if producto is None:
                return "Producto no encontrado."
            
            paciente = Paciente.buscar_por_id(paciente_id)
            if paciente is None:
                return "Paciente no encontrado."
            
            ok, mensaje = producto.vender(cantidad, paciente_id)
            if ok:
                return f"Venta exitosa: {cantidad} x {producto.pr_tipo} para {paciente.pa_nombre}. {mensaje}"
            else:
                return f"No se pudo realizar la venta: {mensaje}"
                
        except Exception as e:
            return f"Error al vender producto: {e}"