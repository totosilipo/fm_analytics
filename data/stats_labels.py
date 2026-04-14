"""
FM DataLab v3 - Stats Labels
==============================
Mapeo de claves internas del CSV a etiquetas legibles para la UI.
Fuente única de verdad — importar desde acá en cualquier módulo que necesite mostrar nombres.
"""

STATS_LABELS: dict[str, str] = {
    'cen c/90':          'Centros completados/90',
    'pos perd/90':       'Posesiones perdidas/90',
    'ent p':             'Entradas %',
    'cen.c/i':           'Centros completados/intentados %',
    'pres c/90':         'Presiones completadas/90',
    'cab g/90':          'Cabezazos ganados/90',
    'rob/90':            'Robos/90',
    'tir/90':            'Tiros/90',
    '% conv':            '% Conversión',
    'asis/90':           'Asistencias/90',
    'oc c/90':           'Ocasiones creadas/90',
    'pases prog/90':     'Pases progresivos/90',
    'xg/90':             'xG/90',
    'asie/90':           'xA/90',
    'pcg %':             '% Pases completados',
    'kp/90':             'Pases clave/90',
    'reg/90':            'Regates/90',
    'entr/90':           'Entradas/90',
    '% de pases':        '% Pases',
    'cab clv/90':        'Cabezazos clave/90',
    'goles por 90 minutos': 'Goles/90',
    'gleq/90':           'Goles de equipo/90',
    'dist/90':           'Distancia recorrida/90',
    'eneq/90':           'Goles encajados del equipo/90',
    'xg -sp/90':         'xG sin penales/90',
    'cen i/90':          'Centros intentados/90',
    'desp/90':           'Despejes/90',
    'dsr/90':            'Disparos bloqueados/90',
    'pres i/90':         'Presiones intentadas/90',
    'pos gan/90':        'Posesiones ganadas/90',
    'rechazos/90':       'Rechazos/90',
    '% de disparos':     '% Disparos a puerta',
    'tirp/90':           'Tiros al palo/90',
    'disparos desde fuera del área por 90 minutos': 'Disparos de lejos/90',
    'ps i/90':           'Pases intentados/90',
    'bal aér/90':        'Balones aéreos/90',
    'cab p/90':          'Cabezazos perdidos/90',
    'pen %':             'Porcentaje de penales convertidos',
    'p clv-jab/90':      'Pases clave en juego abierto/90',
}


def label(stat: str) -> str:
    """Retorna la etiqueta legible de una stat. Si no existe, retorna la clave tal cual."""
    return STATS_LABELS.get(stat, stat)


def label_cols(cols: list[str]) -> dict[str, str]:
    """
    Dado una lista de claves, retorna un dict {clave: etiqueta}
    listo para usar en df.rename(columns=...) o st.column_config.
    Solo incluye las claves que tienen mapeo definido.
    """
    return {col: STATS_LABELS[col] for col in cols if col in STATS_LABELS}
