#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import cfl
import cnf



non_cnf_grammar = cfl.parse_cfg("""
WORD -> SYLLABLE | WORD SYLL_BOUNDARY SYLLABLE
SYLL_BOUNDARY -> ' '


SYLLABLE -> ONSET RIME 

RIME -> NUCLEUS CODA | DIPHTHONG

NUCLEUS -> VOWEL 

ONSET -> STOP LIQUID | FRICATIVE LIQUID | STOP | FRICATIVE | LIQUID | NASAL 
ONSET -> AFFRICATE LIQUID | AFFRICATE
CODA -> LIQUID NASAL | LIQUID FRICATIVE | LIQUID STOP | LIQUID | NASAL 
CODA -> FRICATIVE | STOP | AFFRICATE | LIQUID AFFRICATE


VOWEL -> MONOPHTHONG | DIPHTHONG 
MONOPHTHONG -> 'ɔ' | 'ɑ' | 'i' | 'u' | 'ɛ' | 'ɪ' | 'ʊ' | 'ʌ' | 'ə' | 'æ'
DIPHTHONG -> 'eɪ' | 'aɪ' | 'oʊ' | 'aʊ' | 'ɔɪ'

GLIDE -> 'j' | 'w'
SYLLABIC_CONSONANT -> 'm̩' | 'n̩' | 'ɹ̩' | 'ɫ̩'
NASAL  -> 'm' | 'n' | 'ŋ'
LIQUID -> 'ɹ' | 'l'
FRICATIVE -> 'f' | 'v' | 'θ' | 'ð' | 's' | 'z' | 'ʃ' | 'ʒ' 
STOP -> 'p' | 'b' | 't' | 'd' | 'k' | 'g'
AFFRICATE -> 'tʃ' | 'dʒ'

""")

grammar = cnf.convert_to_cnf(non_cnf_grammar)
assert grammar.is_chomsky_normal_form()

generator = cfl.CFLGenerator(grammar)

def main(args):
    if args:
        num_phones = int(args[0])
    else:
        num_phones = 50

    print ''.join(generator.generate(num_phones))

if __name__ == '__main__':
    main(sys.argv[1:])
