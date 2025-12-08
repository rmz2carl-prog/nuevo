from db_connection import get_conn
import hashlib

def hash_password(password: str) -> str:
    if password is None:
        return None
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class Admin:
    def __init__(self, ad_clave, ad_nom, ad_correo, ad_contraseña):
        self.ad_clave = ad_clave
        self.ad_nom = ad_nom
        self.ad_correo = ad_correo
        self.ad_contraseña = ad_contraseña

    @classmethod
    def crear(cls, ad_nom, ad_correo, ad_contraseña):
        conn = get_conn()
        try:
            cur = conn.cursor()
            pwd_hash = hash_password(ad_contraseña)
            cur.execute(
                "INSERT INTO admin (ad_nom, ad_correo, ad_contraseña) VALUES (%s, %s, %s)",
                (ad_nom, ad_correo, pwd_hash)
            )
            conn.commit()
            ad_clave = cur.lastrowid
            return cls(ad_clave, ad_nom, ad_correo, pwd_hash)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT ad_clave, ad_nom, ad_correo, ad_contraseña FROM admin ORDER BY ad_nom")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3]) for r in rows]
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_correo(cls, ad_correo):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT ad_clave, ad_nom, ad_correo, ad_contraseña FROM admin WHERE ad_correo = %s", (ad_correo,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3]) if r else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def autenticar(cls, ad_correo, ad_contraseña):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT ad_clave, ad_nom, ad_correo, ad_contraseña FROM admin WHERE ad_correo = %s", (ad_correo,))
            r = cur.fetchone()
            if not r:
                return None
            stored_hash = r[3]
            if stored_hash is None:
                return None
            if hash_password(ad_contraseña) == stored_hash:
                return cls(r[0], r[1], r[2], r[3])
            return None
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"{self.ad_nom} ({self.ad_correo})"

class Especialista:
    def __init__(self, es_clave, es_nombre, es_correo, es_contraseña, es_padesig, ad_clave):
        self.es_clave = es_clave
        self.es_nombre = es_nombre
        self.es_correo = es_correo
        self.es_contraseña = es_contraseña
        self.es_padesig = es_padesig
        self.ad_clave = ad_clave

    @classmethod
    def crear(cls, es_nombre, es_correo, es_contraseña, es_padesig, ad_clave):
        conn = get_conn()
        try:
            cur = conn.cursor()
            pwd_hash = hash_password(es_contraseña)
            cur.execute(
                "INSERT INTO especialista (es_nombre, es_correo, es_contraseña, es_padesig, ad_clave) VALUES (%s, %s, %s, %s, %s)",
                (es_nombre, es_correo, pwd_hash, es_padesig, ad_clave)
            )
            conn.commit()
            es_clave = cur.lastrowid
            return cls(es_clave, es_nombre, es_correo, pwd_hash, es_padesig, ad_clave)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT es_clave, es_nombre, es_correo, es_contraseña, es_padesig, ad_clave FROM especialista ORDER BY es_nombre")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_correo(cls, es_correo):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT es_clave, es_nombre, es_correo, es_contraseña, es_padesig, ad_clave FROM especialista WHERE es_correo = %s", (es_correo,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3], r[4], r[5]) if r else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def autenticar(cls, es_correo, es_contraseña):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT es_clave, es_nombre, es_correo, es_contraseña, es_padesig, ad_clave FROM especialista WHERE es_correo = %s", (es_correo,))
            r = cur.fetchone()
            if not r:
                return None
            stored_hash = r[3]
            if stored_hash is None:
                return None
            if hash_password(es_contraseña) == stored_hash:
                return cls(r[0], r[1], r[2], r[3], r[4], r[5])
            return None
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"{self.es_nombre} ({self.es_correo}) - Pacientes designados: {self.es_padesig}"

class Paciente:
    def __init__(self, pa_clave, pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pa_contraseña, pa_sesemana, es_clave):
        self.pa_clave = pa_clave
        self.pa_nombre = pa_nombre
        self.pa_tdiscapacidad = pa_tdiscapacidad
        self.pa_fnac = pa_fnac
        self.pa_correo = pa_correo
        self.pa_contraseña = pa_contraseña
        self.pa_sesemana = pa_sesemana
        self.es_clave = es_clave

    @classmethod
    def crear(cls, pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pa_contraseña, pa_sesemana, es_clave):
        conn = get_conn()
        try:
            cur = conn.cursor()
            pwd_hash = hash_password(pa_contraseña)
            cur.execute(
                "INSERT INTO paciente (pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pa_contraseña, pa_sesemana, es_clave) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pwd_hash, pa_sesemana, es_clave)
            )
            conn.commit()
            pa_clave = cur.lastrowid
            return cls(pa_clave, pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pwd_hash, pa_sesemana, es_clave)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT pa_clave, pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pa_contraseña, pa_sesemana, es_clave FROM paciente ORDER BY pa_nombre")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in rows]
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_correo(cls, pa_correo):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT pa_clave, pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pa_contraseña, pa_sesemana, es_clave FROM paciente WHERE pa_correo = %s", (pa_correo,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) if r else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, pa_clave):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT pa_clave, pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pa_contraseña, pa_sesemana, es_clave FROM paciente WHERE pa_clave = %s", (pa_clave,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) if r else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def autenticar(cls, pa_correo, pa_contraseña):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT pa_clave, pa_nombre, pa_tdiscapacidad, pa_fnac, pa_correo, pa_contraseña, pa_sesemana, es_clave FROM paciente WHERE pa_correo = %s", (pa_correo,))
            r = cur.fetchone()
            if not r:
                return None
            stored_hash = r[5]
            if stored_hash is None:
                return None
            if hash_password(pa_contraseña) == stored_hash:
                return cls(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7])
            return None
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"{self.pa_nombre} - {self.pa_tdiscapacidad} - {self.pa_sesemana} sesiones/semana"