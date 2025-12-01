#!/usr/bin/env python3
"""
Transforma un CSV de tres columnas (intent,type,text) a un CSV con columnas
intent_name,training_phrases,responses (separador '||' para múltiples items).
"""
import csv
import collections
import argparse

def prepare(in_path, out_path):
    intents = collections.defaultdict(lambda: {'training': [], 'response': []})
    with open(in_path, newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        headers = next(reader)
        # detect header style
        # support headers like: intent,type,text
        for row in reader:
            if not row or len(row) < 3:
                continue
            intent = row[0].strip()
            typ = row[1].strip().lower()
            text = row[2].strip()
            if typ.startswith('train'):
                intents[intent]['training'].append(text)
            elif typ.startswith('resp'):
                intents[intent]['response'].append(text)
    # write out
    with open(out_path, 'w', newline='', encoding='utf-8') as outfh:
        writer = csv.writer(outfh)
        writer.writerow(['intent_name','training_phrases','responses'])
        for intent, data in intents.items():
            training = '||'.join(data['training'])
            responses = '||'.join(data['response'])
            writer.writerow([intent, training, responses])
    print('Wrote prepared CSV to', out_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in', dest='in_path', default='./dialogflow/intents.csv')
    parser.add_argument('--out', dest='out_path', default='./dialogflow/intents_prepared.csv')
    args = parser.parse_args()
    prepare(args.in_path, args.out_path)
