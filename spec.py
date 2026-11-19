# -*- coding: utf-8 -*-
"""Especificacion de capas para Corne (Pilot W-CORNE) con SO en layout 'es'.

Cada tecla es una tupla (keycode_vial, etiqueta_para_el_diagrama).
La matriz es 4 filas x 12 columnas, igual que el .vil original:
  - columnas 0..5  = mitad izquierda, de meñique (0) hacia el centro (5)
  - columnas 6..11 = mitad derecha,  del centro (6) hacia el meñique (11)
  - HOLE = posicion sin tecla fisica (-1 en el .vil): [2][6] y [3][2]
"""

HOLE = ("-1", "")
___ = ("KC_TRNS", "▽")

L0 = [
    [("KC_ESCAPE","Esc"), ("KC_Q","Q"), ("KC_W","W"), ("KC_E","E"), ("KC_R","R"), ("KC_T","T"),
     ("KC_RCTRL","Ctrl"), ("KC_Y","Y"), ("KC_U","U"), ("KC_I","I"), ("KC_O","O"), ("KC_P","P")],
    [("KC_CAPSLOCK","Caps"), ("KC_A","A"), ("KC_S","S"), ("KC_D","D"), ("KC_F","F"), ("KC_G","G"),
     ("KC_RSHIFT","Shift"), ("KC_H","H"), ("KC_J","J"), ("KC_K","K"), ("KC_L","L"), ("KC_SCOLON","Ñ")],
    [("KC_LSHIFT","Shift"), ("KC_Z","Z"), ("KC_X","X"), ("KC_C","C"), ("KC_V","V"), ("KC_B","B"),
     HOLE, ("KC_N","N"), ("KC_M","M"), ("KC_COMMA",", ;"), ("KC_DOT",". :"), ("KC_SLASH","- _")],
    [("KC_LALT","Alt"), ("KC_TAB","Tab"), HOLE, ("KC_LCTRL","Ctrl"), ("MO(1)","NUM\nNAV"), ("KC_ENTER","Enter"),
     ("KC_SPACE","Space"), ("MO(2)","SYM"), ("KC_RGUI","Super"), ("KC_BSPACE","Bksp"), ("KC_QUOTE","´ ¨"), ("KC_DELETE","Supr")],
]

L1 = [  # NUM / NAV  -- pulgar izquierdo
    [("KC_TAB","Tab"), ("KC_1","1"), ("KC_2","2"), ("KC_3","3"), ("KC_4","4"), ("KC_5","5"),
     ___, ("KC_6","6"), ("KC_7","7"), ("KC_8","8"), ("KC_9","9"), ("KC_0","0")],
    [___, ("KC_LGUI","Super"), ("KC_LALT","Alt"), ("KC_LSHIFT","Shift"), ("KC_LCTRL","Ctrl"), ("KC_TAB","Tab"),
     ("KC_RALT","AltGr"), ("KC_LEFT","←"), ("KC_DOWN","↓"), ("KC_UP","↑"), ("KC_RIGHT","→"), ("KC_INSERT","Ins")],
    [___, ("LCTL(KC_Z)","Undo"), ("LCTL(KC_X)","Cut"), ("LCTL(KC_C)","Copy"), ("LCTL(KC_V)","Paste"), ("LCTL(LSFT(KC_Z))","Redo"),
     HOLE, ("KC_HOME","Home"), ("KC_PGDOWN","PgDn"), ("KC_PGUP","PgUp"), ("KC_END","End"), ("KC_APPLICATION","Menu")],
    [___, ___, HOLE, ___, ___, ___,
     ___, ("MO(3)","FN"), ___, ___, ___, ___],
]

L2 = [  # SYM -- pulgar derecho
    [("TG(4)","Game"), ("LSFT(KC_1)","!"), ("LSFT(KC_2)","\""), ("RALT(KC_3)","#"), ("LSFT(KC_4)","$"), ("LSFT(KC_5)","%"),
     ___, ("LSFT(KC_6)","&"), ("LSFT(KC_7)","/"), ("LSFT(KC_8)","("), ("LSFT(KC_9)",")"), ("LSFT(KC_0)","=")],
    [___, ("RALT(KC_GRAVE)","\\"), ("LSFT(KC_SLASH)","_"), ("KC_SLASH","-"), ("KC_RBRACKET","+"), ("LSFT(KC_RBRACKET)","*"),
     ("RALT(KC_1)","|"), ("RALT(KC_QUOTE)","{"), ("RALT(KC_LBRACKET)","["), ("RALT(KC_RBRACKET)","]"), ("RALT(KC_BSLASH)","}"), ("KC_MINUS","'")],
    [___, ("KC_LBRACKET","` +esp"), ("LSFT(KC_LBRACKET)","^ +esp"), ("KC_NONUS_BSLASH","<"), ("LSFT(KC_NONUS_BSLASH)",">"), ("RALT(KC_4)","~"),
     HOLE, ("RALT(KC_2)","@"), ("LSFT(KC_DOT)",":"), ("LSFT(KC_COMMA)",";"), ("LSFT(KC_MINUS)","?"), ("LSFT(KC_EQUAL)","¿")],
    [___, ___, HOLE, ___, ("MO(3)","FN"), ___,
     ___, ___, ___, ___, ___, ___],
]

L3 = [  # FN / MEDIA / SYS -- ambos pulgares
    [___, ("KC_F1","F1"), ("KC_F2","F2"), ("KC_F3","F3"), ("KC_F4","F4"), ("KC_F5","F5"),
     ___, ("KC_F6","F6"), ("KC_F7","F7"), ("KC_F8","F8"), ("KC_F9","F9"), ("KC_F10","F10")],
    [___, ("KC_F11","F11"), ("KC_F12","F12"), ("KC_GRAVE","º ª"), ("RALT(KC_E)","€"), ("RALT(KC_6)","¬"),
     ___, ("KC_MEDIA_PREV_TRACK","Prev"), ("KC_AUDIO_VOL_DOWN","Vol-"), ("KC_AUDIO_VOL_UP","Vol+"), ("KC_MEDIA_NEXT_TRACK","Next"), ("KC_AUDIO_MUTE","Mute")],
    [___, ("KC_BSLASH","ç Ç"), ("KC_EQUAL","¡ ¿"), ("RALT(KC_5)","½"), ("LSFT(KC_3)","·"), ("RALT(KC_NONUS_BSLASH)","« »"),
     HOLE, ("KC_MEDIA_PLAY_PAUSE","Play"), ("KC_PSCREEN","PrtSc"), ("KC_INSERT","Ins"), ("KC_NUMLOCK","NumLk"), ("KC_SCROLLLOCK","ScrLk")],
    [___, ___, HOLE, ___, ___, ___,
     ___, ___, ___, ___, ___, ___],
]

def _right_half_of(layer, override=None):
    """Mitad derecha (columnas 6..11) copiada de otra capa; override = {(r, c): tecla}."""
    override = override or {}
    return [[override.get((r, c), layer[r][c]) for c in range(6, 12)] for r in range(4)]


# Capas de juego. Se entra y se sale con SYM + Esc (TG(4)), como un interruptor.
# GAME es la capa 4: queda POR ENCIMA de SYM (2), asi que dentro del juego el pulgar
# de SYM apunta a la capa 6 (copia de SYM) para que SYM + Esc siga llegando a TG(4).
_g_right = _right_half_of(L0, {(3, 7): ("MO(6)", "SYM")})
L4 = [  # GAME -- mano izquierda en el juego, derecha para el chat
    [("KC_ESCAPE","Esc"), ("KC_Q","Q"), ("KC_W","W"), ("KC_E","E"), ("KC_R","R"), ("KC_T","T")] + _g_right[0],
    [("KC_LSHIFT","Shift"), ("KC_A","A"), ("KC_S","S"), ("KC_D","D"), ("KC_F","F"), ("KC_G","G")] + _g_right[1],
    [("KC_LALT","Alt"), ("KC_Z","Z"), ("KC_X","X"), ("KC_C","C"), ("KC_V","V"), ("KC_B","B")] + _g_right[2],
    # [3][0] y [3][1] = columna interior izquierda (junto a T y G): teclas que se pulsan
    # sueltas, asi el estiramiento no importa; los modificadores quedan en meñique y pulgar
    [("KC_TAB","Tab"), ("KC_ENTER","Enter"), HOLE, ("KC_LCTRL","Ctrl"), ("KC_SPACE","Space"), ("MO(5)","G-FN")] + _g_right[3],
]

L5 = [  # GAME-FN -- pulgar izquierdo interior, solo dentro de GAME
    [___, ("KC_1","1"), ("KC_2","2"), ("KC_3","3"), ("KC_4","4"), ("KC_5","5")] + [___] * 6,
    [___, ("KC_F1","F1"), ("KC_F2","F2"), ("KC_F3","F3"), ("KC_F4","F4"), ("KC_F5","F5")] + [___] * 6,
    [___, ("KC_6","6"), ("KC_7","7"), ("KC_8","8"), ("KC_9","9"), ("KC_0","0"), HOLE] + [___] * 5,
    [___, ___, HOLE, ___, ___, ___] + [___] * 6,
]

# SYM dentro del juego: igual que L2 (con el mismo TG(4) en Esc para salir), salvo
# que no lleva a FN: en GAME esa tecla es Space.
L6 = [row[:] for row in L2]
L6[3][4] = ___

LAYERS = [
    ("0 · BASE", "QWERTY español (SO en layout 'es')", L0),
    ("1 · NUM / NAV", "pulgar izquierdo", L1),
    ("2 · SYM", "pulgar derecho", L2),
    ("3 · FN / MEDIA / SYS", "ambos pulgares", L3),
    ("4 · GAME", "SYM + Esc entra y sale", L4),
    ("5 · GAME-FN", "pulgar izq. interior, dentro de GAME", L5),
    ("6 · SYM (en GAME)", "pulgar derecho, dentro de GAME", L6),
]

# Posiciones cuya ubicacion fisica esta SIN CONFIRMAR (ver PLAN.md).
# Confirmadas con la pestaña Keymap de Vial (46 teclas, 3 pulgares por lado):
#   [3][0], [3][1]            = columna interior izquierda (junto a T y G), arriba / abajo
#   [0][6], [1][6]            = columna interior derecha (junto a Y y H), arriba / abajo
#   [3][9], [3][10], [3][11]  = columna exterior derecha (meñique, junto a P/Ñ/-)
UNCONFIRMED = set()
