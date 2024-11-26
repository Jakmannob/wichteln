import os
import time
import random
import argparse
from fpdf import FPDF


parser = argparse.ArgumentParser(prog='Wichtel distribution',
        description='A small tool to help with the generation of a secret santa mapping')
parser.add_argument(
    'name_file',
    type=str,
    help='The path to the file containing participant names.'
)
parser.add_argument(
    'output_dir',
    type=str,
    help='The name of a directory in which the output files will be stored.'
)
parser.add_argument(
    '--permutations',
    type=str,
    default='(-1,1)',
    help='A list of tuples specifying the cycles of the permutation. The first ' +
        'entry of the tuple is the size of the cycle and the second is the count ' +
        'of how often such a cycle is in the permutation. If one of these is ' +
        '-1, it will be assumed.'
)
parser.add_argument(
    '--output_type',
    type=str,
    choices=['txt', 'pdf'],
    default='pdf',
    help='The format of the output file'
)
parser.add_argument(
    '--seed',
    type=int,
    default=-1,
    help='If you want to be able to be in control of the RNG, put a positive seed here.'
)
parser.add_argument(
    '--lang',
    type=str,
    choices=['english', 'german'],
    default='english',
    help='You can set the language with this.'
)


class WichtelDistribution:

    def __init__(self, input_name_file, output_directory, permutations,
            output_type, seed, language):
        self.input_name_file = input_name_file
        self._parse_input_file()
        self.output_directory = output_directory
        self.permutations = permutations
        if isinstance(self.permutations, str):
            self._parse_permutations()
        self.output_type = output_type
        self.seed = seed
        self.language = language

        self._shuffle_names()

    def _parse_input_file(self):
        self.names = []
        with open(self.input_name_file, 'r') as name_file:
            for line in name_file.readlines():
                line = line.strip()
                if len(line) <= 0:
                    continue
                if line.startswith('#'):
                    continue
                self.names.append(line)

    def _shuffle_names(self):
        if self.seed < 0:
            random.shuffle(self.names)
            return
        random.Random(self.seed).shuffle(self.names)

    def _verify_permutations(self, unverified):
        n = len(self.names)
        used_n = n
        assume_count = 0
        assume_tuple = None
        fixed_permutations = []

        for size, count in unverified:
            if size == 0 or count == 0:
                continue
            if size < 0 or count < 0:
                assume_count += 1
                assume_tuple = (size, count)
                continue
            used_n -= count * size
            fixed_permutations.append((size, count))

        if used_n < 0:
            raise ValueError('Please check your permutations, they are not correct.')
        if assume_count > 1:
            raise ValueError('Please use -1 at most once when generating permutations.')
        if assume_tuple is not None:
            if assume_tuple[0] == -1:
                assume_tuple = (used_n//assume_tuple[1], assume_tuple[1])
            if assume_tuple[1] == -1:
                assume_tuple = (assume_tuple[0], used_n//assume_tuple[0])
            used_n -= assume_tuple[0] * assume_tuple[1]
            if used_n != 0:
                raise ValueError('Please check your permutations, they are not correct.')
            fixed_permutations.append(assume_tuple)

        return fixed_permutations

    def _parse_permutations(self):
        unverified = self.permutations.split('(')[1:]
        unverified = [part.split(')')[0] for part in unverified]
        unverified = [(int(part.split(',')[0]), int(part.split(',')[1])) for part in unverified]
        self.permutations = self._verify_permutations(unverified)

    def _sub_draw(self, names):
        names.append(names[0])
        drawn = dict()
        for i, gifter in enumerate(names[:-1]):
            gifted = names[i+1]
            drawn[gifter] = gifted
        return drawn

    def draw(self):
        drawn = dict()
        position = 0
        for size, count in self.permutations:
            for i in range(count):
                drawn = drawn | self._sub_draw(self.names[position:position+size])
                position += size
        return drawn

    def _get_write_text(self, gifter, gifted):
        if self.language == 'english':
            return f'You are secret santa for: {gifted}'
        elif self.language == 'german':
            return f'Du machst ein Geschenk für: {gifted}'
        return gifted

    def _write_single_pdf(self, gifter, gifted):
        text = self._get_write_text(gifter, gifted)

        pdf = FPDF()
        pdf.set_xy(0, 0)
        pdf.set_font('Helvetica', size=13, style='B')
        text_width = int(pdf.get_string_width(text))+20
        text_height = 22 
        pdf.add_page(format=(text_width, text_height))
        pdf.set_left_margin(0)
        pdf.set_right_margin(0)
        pdf.set_top_margin(0)
        pdf.set_auto_page_break(auto=0, margin=0)
        pdf.cell(0, 0, text=text, align='C')
        pdf.output(os.path.join(self.output_directory, f'{gifter}.pdf'))

    def _write_single_txt(self, gifter, gifted):
        with open(os.path.join(self.output_directory, f'{gifter}.txt'),
                'w') as output_file:
            output_file.write(self._get_write_text(gifter, gifted))

    def write(self, distribution):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        for gifter, gifted in distribution.items():
            if self.output_type == 'pdf':
                self._write_single_pdf(gifter, gifted)
            elif self.output_type == 'txt':
                self._write_single_txt(gifter, gifted)

    def draw_and_write(self):
        self.write(self.draw())


if __name__ == '__main__':
    args = parser.parse_args()
    distribution = WichtelDistribution(args.name_file, args.output_dir,
            args.permutations, args.output_type, args.seed, args.lang)
    distribution.draw_and_write()
