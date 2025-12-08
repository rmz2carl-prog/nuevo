from db_connection import get_conn

class Productos:
    def __init__(self, pr_clave, pr_tipo, pr_precio, pr_cantidad):
        self.pr_clave = pr_clave
        self.pr_tipo = pr_tipo
        self.pr_precio = pr_precio
        self.pr_cantidad = pr_cantidad

    @classmethod
    def crear(cls, pr_tipo, pr_precio, pr_cantidad=0):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO productos (pr_tipo, pr_precio, pr_cantidad) VALUES (%s, %s, %s)",
                (pr_tipo, pr_precio, pr_cantidad)
            )
            conn.commit()
            pr_clave = cur.lastrowid
            return cls(pr_clave, pr_tipo, pr_precio, pr_cantidad)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT pr_clave, pr_tipo, pr_precio, pr_cantidad FROM productos ORDER BY pr_tipo")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3]) for r in rows]
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_tipo(cls, pr_tipo):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT pr_clave, pr_tipo, pr_precio, pr_cantidad FROM productos WHERE pr_tipo = %s", (pr_tipo,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3]) if r else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, pr_clave):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT pr_clave, pr_tipo, pr_precio, pr_cantidad FROM productos WHERE pr_clave = %s", (pr_clave,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3]) if r else None
        finally:
            cur.close()
            conn.close()

    def vender(self, cantidad, paciente_id):
        """Vende una cantidad específica del producto a un paciente"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            
            # Verifica stock disponible
            if self.pr_cantidad < cantidad:
                return False, "Stock insuficiente"
            
            # Actualiza stock
            nueva_cantidad = self.pr_cantidad - cantidad
            cur.execute("UPDATE productos SET pr_cantidad = %s WHERE pr_clave = %s", 
                       (nueva_cantidad, self.pr_clave))
            
            # Registra la venta
            total = self.pr_precio * cantidad
            cur.execute(
                "INSERT INTO ventas (ve_cantidad, ve_total, pa_clave, pr_clave) VALUES (%s, %s, %s, %s)",
                (cantidad, total, paciente_id, self.pr_clave)
            )
            
            conn.commit()
            self.pr_cantidad = nueva_cantidad
            return True, f"Venta realizada: {cantidad} x {self.pr_tipo} - Total: ${total}"
            
        except Exception as e:
            conn.rollback()
            return False, f"Error en la venta: {e}"
        finally:
            cur.close()
            conn.close()
            
    def __str__(self):
        return f"{self.pr_tipo} - ${self.pr_precio} - Stock: {self.pr_cantidad}"

class Terapia:
    def __init__(self, te_clave, te_finicio, te_sescom, pa_clave, es_clave):
        self.te_clave = te_clave
        self.te_finicio = te_finicio
        self.te_sescom = te_sescom
        self.pa_clave = pa_clave
        self.es_clave = es_clave

    @classmethod
    def crear(cls, te_finicio, te_sescom, pa_clave, es_clave):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO terapia (te_finicio, te_sescom, pa_clave, es_clave) VALUES (%s, %s, %s, %s)",
                (te_finicio, te_sescom, pa_clave, es_clave)
            )
            conn.commit()
            te_clave = cur.lastrowid
            return cls(te_clave, te_finicio, te_sescom, pa_clave, es_clave)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT te_clave, te_finicio, te_sescom, pa_clave, es_clave FROM terapia ORDER BY te_finicio DESC")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"Terapia iniciada: {self.te_finicio} - Sesiones: {self.te_sescom}"