#!/usr/bin/env python3

"""
 Copyright (c) 2019-2020, Ontario Institute for Cancer Research (OICR).

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: Linda Xiang <linda.xiang@oicr.on.ca>
         Junjun Zhang <junjun.zhang@oicr.on.ca>
"""

import os
import sys
from argparse import ArgumentParser
import subprocess
from multiprocessing import cpu_count
import tarfile
import glob
import json


def collect_metrics(args):
  # generate stats_args string
  stats_args = [
    '--reference', args.reference,
    '-@', str(args.cpus),
    '-r', args.reference,
    '--split', 'RG',
    '-P', os.path.join(os.getcwd(), os.path.basename(args.seq))
  ]

  try:
    cmd = ['samtools', 'stats'] + stats_args + [args.seq]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
  except Exception as e:
    sys.exit("Error: %s. 'samtools stats' failed: %s\n" % (e, args.seq))

  with open(os.path.join(os.getcwd(), os.path.basename(args.seq)+".bamstat"), 'w') as f:
    f.write(p.stdout.decode('utf-8'))

  extra_info = {}
  collected_sum_fields = {
    'raw total sequences': 'total_reads',
    'reads mapped': 'mapped_reads',
    'reads paired': 'paired_reads',
    'reads properly paired': 'properly_paired_reads',
    'pairs on different chromosomes': 'pairs_on_different_chromosomes',
    'total length': 'total_bases',
    'bases mapped (cigar)': 'mapped_bases_cigar',
    'mismatches': 'mismatch_bases',
    'error rate': 'error_rate',
    'bases duplicated': 'duplicated_bases',
    'insert size average': 'average_insert_size',
    'average length': 'average_length'
  }
  with open(os.path.join(os.getcwd(), os.path.basename(args.seq)+".bamstat"), 'r') as f:
    for row in f:
      if not row.startswith('SN\t'): continue
      cols = row.replace(':', '').strip().split('\t')

      if cols[1] not in collected_sum_fields: continue
      extra_info.update({
          collected_sum_fields[cols[1]]: float(cols[2]) if ('.' in cols[2] or 'e' in cols[2]) else int(cols[2])
        })

  p = subprocess.run('samtools --version | grep samtools', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, shell=True)
  tool_ver = "samtools:stats@%s" % p.stdout.decode('utf-8').strip().split(' ')[-1]
  extra_info.update({ "tool": tool_ver })
  with open(os.path.basename(args.seq) + '.extra_info.json', "w") as j:
    j.write(json.dumps(extra_info, indent=2))

  # make tar gzip ball of the *.bamstat files
  tarfile_name = os.path.basename(args.seq)+'.qc_metrics.tgz'
  with tarfile.open(tarfile_name, "w:gz") as tar:
    for statsfile in glob.glob(os.path.join(os.getcwd(), "*.bamstat")) + glob.glob(os.path.join(os.getcwd(), "*.extra_info.json")):
      tar.add(statsfile, arcname=os.path.basename(statsfile))


def main():
  parser = ArgumentParser()
  parser.add_argument("-s", "--seq", dest="seq", help="Aligned sequence file", type=str, required=True)
  parser.add_argument('-r', '--reference', dest='reference', type=str, help='reference fasta', required=True)
  parser.add_argument('-n', '--cpus', dest='cpus', type=int, help='number of cpu cores', default=cpu_count())

  args = parser.parse_args()

  collect_metrics(args)


if __name__ == '__main__':
  main()