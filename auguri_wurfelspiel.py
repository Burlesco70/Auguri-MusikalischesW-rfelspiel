# coding:utf-8
# Copyright 2018 Moisés Cachay
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Musikalisches Würfelspiel
# https://dice.humdrum.org/

import os
import random
import re
import subprocess
import sys
from dotenv import load_dotenv

def path(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def get_notes(part):
    return map(lambda i: (i[0], i[-1]),
               re.findall(r'\s+% (\d+(\.\d)?)\s*(.*)', part))


def parse_score(score):
    '''
    Divisione del file "modello" score.ly in parti logiche
    usando le espressioni regolari
    '''
    (header, first_separator, upper, second_separator, lower,
     third_separator, footer) = re.split(
        r'(.*clef treble\n|'
        r'\s*}\n\s*\\new Staff = "down" {\n\s*\\clef bass\n|'
        r'\s*}\n\s*>>.*)',
        score
    )

    notes = {
        number: (upper_notes, lower_notes,)
        for (number, upper_notes,), (_, lower_notes,)
        in zip(get_notes(upper), get_notes(lower))
    }

    spacer = re.findall(r'( +)\\clef', score)[0]

    return (header, first_separator, second_separator, third_separator,
            footer, spacer, notes)


def get_first_half_fragment(measure, part):
    '''Prime 8 battute'''
    return (
        ('096', '022', '141', '041', '105', '122', '011', '030',),
        ('032', '006', '128', '063', '146', '046', '134', '081',),
        ('069', '095', '158', '013', '153', '055', '110', '024',),
        ('040', '017', '113', '085', '161', '002', '159', '100',),
        ('148', '074', '163', '045', '080', '097', '036', '107',),
        ('104', '157', '027', '167', '154', '068', '118', '091',),
        ('152', '060', '171', '053', '099', '133', '021', '127',),
        ('119', '084', '114', '050', '140', '086', '169', '094',),
        ('098', '142', '042', '156', '075', '129', '062', '123',),
        ('003', '087', '165', '061', '135', '047', '147', '033',),
        ('054', '130', '010', '103', '028', '037', '106', '005',),
    )[part][measure]


def get_second_half_fragment(measure, part):
    '''Seconde 8 battute'''
    return (
        ('070', '121', '026', '009', '112', '049', '109', '014',),
        ('117', '039', '126', '056', '174', '018', '116', '083',),
        ('066', '139', '015', '132', '073', '058', '145', '079',),
        ('090', '176', '007', '034', '067', '160', '052', '170',),
        ('025', '143', '064', '125', '076', '136', '001', '093',),
        ('138', '071', '150', '029', '101', '162', '023', '151',),
        ('016', '155', '057', '175', '043', '168', '089', '172',),
        ('120', '088', '048', '166', '051', '115', '072', '111',),
        ('065', '077', '019', '082', '137', '038', '149', '008',),
        ('102', '004', '031', '164', '144', '059', '173', '078',),
        ('035', '020', '108', '092', '012', '124', '044', '131',),
    )[part][measure]


def get_factors(n):
    '''
    Funzione ricorsiva per ottenere la lista di "lanci dado"
    con valori tra 0 e 10 (11 valori)
    Se n < 11: ritorna il valore; altrimenti ritorna il valore % 11 e 
    richiama ricorsivamente sul valore intero della divisione per 11
    '''
    if n < 11:
        return [n]
    else:
        return [n % 11] + get_factors(n // 11)


def get_parts(number=None):
    '''
    Calcola numero e simula i 16 lanci di dado (factors)
    '''
    factors = get_factors(number)
    # Prendo 16 "estrazioni", perchè le battute sono 16
    if len(factors) > 16:
        factors = factors[:16]
    else:
        # Se ci sono meno estrazioni, aggiunge sempre 0 in coda
        factors = factors + [0] * (16 - len(factors))
    return number, factors


def update_header(header, number, parts, dedicated_to, title, greetings_from):
    '''
    Sostituisce il placeholder #id# con quello che si vuole
    Originariamente il numero casuale  e la sequenza "lancio dadi" calcolata
    '''
    if not dedicated_to:
        dedicated = 'Unicamente generato'
    else:
        dedicated = 'Unicamente generato per ' + dedicated_to
    header = header.replace('#title#', title)
    header = header.replace("#gf#", greetings_from) 
    return header.replace(
        '#id#',
        '{}: {}'.format(dedicated + ", con la combinazione", ','.join(map(lambda p: str(p + 2), parts)))
    )


def generate_part(first_half, repeat_notes, second_half, half, spacer):
    '''
    Funzione richiamata due volte dalla generate_score
    La prima volta "half" vale 0, la seconda 1
    first_half, repeat_notes, second_half sono liste di tuple corrispondenti alle battute
    ripettivamente di 7, 2 e 8 elementi
    '''
    return \
        '{}\\repeat volta 2 {{\n{}'.format(spacer, spacer) + \
        '\n{}'.format(spacer).join(map(lambda note: note[half], first_half)) + \
        '}}\n{}'.format(spacer) + \
        '\\alternative {{\n{}'.format(spacer) + \
        '    {{ {} | }}'.format(repeat_notes[0][half]) + \
        '\n{}'.format(spacer) + \
        '    {{ {} | }}'.format(repeat_notes[1][half]) + \
        '\n{}'.format(spacer) + \
        '}}'.format(spacer) + \
        '\n{}{}'.format(spacer, '| \mark "Trio"') + \
        '\n{}'.format(spacer) + \
        '\n{}'.format(spacer).join(map(lambda note: note[half], second_half)) + \
        '\n{}\\bar "|."'.format(spacer)


def generate_score(parts=None, number=None, dedicated_to=None, title=None, greetings_from=None):
    '''
    Genera lo spartito
    '''
    if not parts:
        number, parts = get_parts(number)
    
    # "parts" contiene i valori dei 16 lanci di dado
    # con valori da 0 a 10 (il lamcio dadi sarebbe da 2 a 12)
    # print(parts)

    # Apre il file con lo spartito con tutte le combinazioni
    with open(path('score.ly'), encoding='utf-8') as s:
        score = s.read()

    # Divisione del file "modello" score.ly in parti logiche
    (header, first_separator, second_separator, third_separator,
     footer, spacer, first_half) = parse_score(score)

    # Prime sette battute
    first_half_notes = list(map(
        lambda part: first_half[get_first_half_fragment(*part)],
        enumerate(parts[:7])
    ))

    # Ottava battuta, quella ripetuta
    repeat_notes = [
        first_half['{}.1'.format(get_first_half_fragment(7, parts[7]))],
        first_half['{}.2'.format(get_first_half_fragment(7, parts[7]))],
    ]

    # Ultime otto battute
    second_half_notes = list(map(
        lambda part: first_half[get_second_half_fragment(*part)],
        enumerate(parts[8:])
    ))

    generated_score = \
        update_header(header, number, parts, dedicated_to, title, greetings_from) + \
        first_separator + \
        generate_part(first_half_notes, repeat_notes, second_half_notes, 0, spacer) + \
        second_separator + \
        generate_part(first_half_notes, repeat_notes, second_half_notes, 1, spacer) + \
        third_separator + \
        footer

    return generated_score, parts, number


def generate_song(parts=None, number=None, dedicated_to=None, title=None, greetings_from=None):
    # Genera lo spartito "score"
    score, parts, number = generate_score(parts=parts, number=number, dedicated_to=dedicated_to, title=title, greetings_from=greetings_from)
    # Nome files di output
    out_file='out'
    if dedicated_to:
        out_file = dedicated_to

    load_dotenv()
    LILYPOND_EXECUTABLE = os.getenv("LILYPOND_EXECUTABLE")
    TIMIDITY_EXECUTABLE = os.getenv("TIMIDITY_EXECUTABLE")
    FFMPEG_EXECUTABLE = os.getenv("FFMPEG_EXECUTABLE")

    # Genera l'immagine png con lo spartito e il file midi
    subprocess.run(
        [LILYPOND_EXECUTABLE,
         '--png',
         '--output={}'.format(path(out_file)),
         '-dresolution=175',
         '-'],
        input=score.encode()
    )

    # Genera il file wav
    subprocess.run([
        TIMIDITY_EXECUTABLE,
        path(out_file + '.mid'),
        '-Ow',
        '-o', path(out_file + '.wav')
    ])

    # Genera il video da png e wav
    subprocess.run([
        FFMPEG_EXECUTABLE,
        '-y',
        '-loop', '1',
        '-i', path(out_file + '.png'),
        '-i', path(out_file + '.wav'),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        '-strict', '-2',
        '-shortest',
        '-vf', r'transpose=1,scale=-2:min(1080\,if(mod(ih\,2)\,ih-1\,ih))',
        path(out_file + '.mp4')
    ])

    return parts, number

if __name__ == '__main__':
    # Parametri per gli auguri
    dedicated_to = None
    title = "Minuetto di Auguri per un meraviglioso 2023"
    greetings_from = "Mario e Maura"
    if len(sys.argv) > 1:
        dedicated_to=sys.argv[1]        
    # Main
    parts, number = generate_song(
        #Anzichè lanciare due dadi per 16 volte... 
        number=random.randint(0, (11**16) - 1),
        dedicated_to=dedicated_to,
        title=title,
        greetings_from=greetings_from
    )

