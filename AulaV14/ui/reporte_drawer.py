"""ui/reporte_drawer.py

Panel tipo "cajón" (drawer) para seleccionar y visualizar reportes sin guardarlos.

Proporciona una interfaz unificada donde el usuario puede elegir entre diferentes
tipos de reportes que se generan y renderizan automáticamente de forma visual,
sin persistencia en la base de datos.

Reportes disponibles:
  1. Calificaciones por Asignatura
  2. Estado de Matrículas
  3. Tareas
  4. Promedios por Estudiante
  5. (Reporte de Coordinador si es coordinador)
  6. (Reporte de Docente si es docente)
"""

import tkinter as tk
from tkinter import ttk
from ui.base import C, ROL_COLOR, scroll_canvas
from ui.shared import render_reporte
from services.reporte_service import DirectorReportes


def panel_reportes_drawer(parent, usuario, repo, guardar_historial=False):
    """Crea un panel con un 'cajón' de reportes seleccionables.
    
    Args:
        parent: Widget padre donde renderizar el panel
        usuario: Usuario actual (objeto de usuario)
        repo: RepositorioAcademico
        guardar_historial: Si True, guarda cada reporte en el historial (para coordinador/admin)
    """
    rol = usuario.obtener_rol()
    color = ROL_COLOR.get(rol, C["accent"])
    
    wrap = tk.Frame(parent, bg=C["bg"])
    wrap.pack(fill="both", expand=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Sección de selección de reportes (el "cajón")
    # ─────────────────────────────────────────────────────────────────────────
    selector_frame = tk.Frame(wrap, bg=C["card"], bd=1, relief="solid")
    selector_frame.pack(fill="x", padx=12, pady=12)
    
    # Título
    header = tk.Frame(selector_frame, bg=color, padx=14, pady=10)
    header.pack(fill="x")
    tk.Label(header, text="📊  Selecciona un tipo de reporte", 
             font=("Segoe UI", 11, "bold"), bg=color, fg=C["white"]).pack(anchor="w")
    
    # Contenedor de opciones
    opciones_frame = tk.Frame(selector_frame, bg=C["card"], padx=14, pady=12)
    opciones_frame.pack(fill="x")
    
    # Variable para almacenar la opción seleccionada
    opcion_var = tk.StringVar(value="calificaciones")
    
    # Definir opciones disponibles según el rol
    opciones = [
        ("calificaciones", "📈  Calificaciones por Asignatura", "Ver notas y aprobaciones"),
        ("matriculas", "📋  Estado de Matrículas", "Resumen de matrículas activas/anuladas"),
        ("tareas", "✅  Tareas y Entregas", "Visión rápida de tareas y entregas"),
        ("promedios", "🎓  Promedios por Estudiante", "Desempeño académico por estudiante"),
    ]
    
    # Agregar opciones específicas por rol
    if rol == "docente":
        opciones.append(("docente", "👨‍🏫  Mi Reporte de Docente", "Progreso de mis alumnos"))
    elif rol == "coordinador":
        opciones.append(("coordinador", "📊  Reporte de Coordinador", "Métricas globales y rendimiento"))
    elif rol == "administrador":
        opciones.append(("administrador", "🛡️  Reporte de Auditoría", "Auditoría y consistencia del sistema"))
    
    # Crear radio buttons para cada opción
    for valor, titulo, descripcion in opciones:
        frame_opcion = tk.Frame(opciones_frame, bg=C["card"])
        frame_opcion.pack(fill="x", pady=6)
        
        rb = tk.Radiobutton(
            frame_opcion, variable=opcion_var, value=valor,
            bg=C["card"], fg=C["text"], activebackground=C["card"],
            activeforeground=color, selectcolor=C["card"],
            font=("Segoe UI", 9)
        )
        rb.pack(side="left", padx=0)
        
        # Etiqueta principal
        tk.Label(frame_opcion, text=titulo, font=("Segoe UI", 10, "bold"),
                 bg=C["card"], fg=C["text"], anchor="w", padx=4).pack(side="left", fill="x", expand=True)
        
        # Descripción pequeña
        tk.Label(frame_opcion, text=descripcion, font=("Segoe UI", 8),
                 bg=C["card"], fg=C["text_sec"], anchor="w", padx=4).pack(side="left", padx=(0, 4))
    
    # Botón de generación
    btn_frame = tk.Frame(selector_frame, bg=C["card"], padx=14, pady=8)
    btn_frame.pack(fill="x")
    
    # Mensaje de estado
    estado_lbl = tk.Label(btn_frame, text="", font=("Segoe UI", 8),
                          bg=C["card"], fg=C["success"])
    estado_lbl.pack(anchor="w", pady=(0, 6))
    
    # Contenedor para el resultado
    resultado_frame = tk.Frame(wrap, bg=C["bg"])
    resultado_frame.pack(fill="both", expand=True, padx=12, pady=12)
    
    director = DirectorReportes(repo)
    
    # Importar ReporteService solo si se va a guardar
    reporte_service = None
    if guardar_historial:
        from services.reporte_service import ReporteService
        reporte_service = ReporteService(repo)
    
    def generar_reporte():
        """Genera el reporte seleccionado y lo renderiza."""
        # Limpiar el contenedor anterior
        for widget in resultado_frame.winfo_children():
            widget.destroy()
        
        estado_lbl.config(text="")
        opcion = opcion_var.get()
        
        try:
            # Generar el reporte según la opción seleccionada
            if opcion == "calificaciones":
                reporte = director.construir_reporte_calificaciones_por_asignatura()
            elif opcion == "matriculas":
                reporte = director.construir_reporte_estado_matriculas()
            elif opcion == "tareas":
                reporte = director.construir_reporte_tareas()
            elif opcion == "promedios":
                reporte = director.construir_reporte_promedios_estudiantes()
            elif opcion == "docente":
                reporte = director.construir_reporte_docente(usuario.email)
            elif opcion == "coordinador":
                reporte = director.construir_reporte_coordinador()
            elif opcion == "administrador":
                reporte = director.construir_reporte_administrador()
            else:
                reporte = None
            
            if reporte:
                # Renderizar el reporte
                render_reporte(resultado_frame, reporte, color_header=color)
                
                # Guardar en historial si está habilitado
                if guardar_historial and reporte_service:
                    registro = reporte_service.registrar_generacion(
                        reporte, tipo=opcion,
                        generado_por=usuario.email, rol_generador=usuario.obtener_rol(),
                    )
                    estado_lbl.config(
                        text=f"✅  Reporte #{registro.id} guardado en historial (visible para el Administrador)"
                    )
        except Exception as e:
            # Mostrar error
            error_frame = tk.Frame(resultado_frame, bg=C["bg"])
            error_frame.pack(fill="both", expand=True)
            tk.Label(error_frame, text="⚠️  Error al generar el reporte",
                     font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["danger"]).pack(pady=10)
            tk.Label(error_frame, text=str(e), font=("Segoe UI", 9),
                     bg=C["bg"], fg=C["text_sec"], wraplength=600,
                     justify="left").pack(padx=20, pady=10)
    
    # Botón "Generar reporte"
    btn_gen = tk.Button(btn_frame, text="🔄  Generar reporte", bg=color, fg=C["white"],
                        font=("Segoe UI", 10, "bold"), padx=16, pady=8,
                        command=generar_reporte, relief="flat", cursor="hand2",
                        activebackground=C["sidebar"], activeforeground=C["white"])
    btn_gen.pack(fill="x")
    
    # Auto-generar el primer reporte
    generar_reporte()
