#!/usr/bin/env nextflow

/*
 * Copyright (c) 2019, Ontario Institute for Cancer Research (OICR).
 *                                                                                                               
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

/*
 * author Junjun Zhang <junjun.zhang@oicr.on.ca>
 */

nextflow.preview.dsl=2
version = '0.1.0.0'

params.ubam = "tests/data/C0HVY_2.lane.bam"
params.container_version = ''


process readGroupUBamQC {
  container "quay.io/icgc-argo/read-group-ubam-qc:read-group-ubam-qc.${params.container_version ?: version}"

  input:
    path ubam

  output:
    path "*.quality_yield_metrics.txt", emit: metrics
    path "*.ubam_info.json", emit: ubam_info

  script:
    """
    read-group-ubam-qc.py -b ${ubam}
    """
}