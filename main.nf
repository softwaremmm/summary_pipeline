#!/usr/bin/env nextflow

workflow {
    //Define ANSI colours for ease
    def ANSI_GREEN = "\033[1;32m"
    def ANSI_RESET = "\033[0m"
    log.info(
        """
        Runtime data:
        ------------------------------------------------------------------------

        Running with profile  ${ANSI_GREEN}${workflow.profile}${ANSI_RESET}
        Running as user       ${ANSI_GREEN}${workflow.userName}${ANSI_RESET}
        Launch directory      ${ANSI_GREEN}${workflow.launchDir}${ANSI_RESET}
        Project directory     ${ANSI_GREEN}${projectDir}${ANSI_RESET}
        """.stripIndent()
    )
    if (params.help) {
        log.info(
            '''
            ========================================================================
            Summary

            Combines output from workflow steps to create a single summary JSON file.

            Parameters:
            ------------------------------------------------------------------------
            --reports  List of paths to reports e.g.
            Path to gatekeeper report (`speciation_report.json`).
            Path to competitive mapping report (`species_comparison_report.json`).
            Path to mykrobe report (`subspecies_report.json`).
            Path to gnomonicus report (`resistance_prediction_report.json`).
            Or glob pattern to find all reports e.g. `sample_reports/*`.
            '''.stripIndent()
        )

        exit(0)
    }

    if (params.reports.contains("*")) {
        reports_ch = Channel.fromPath(params.reports).collect().map { ["sample", it] }
    } else {
        reports_list = params.reports?.split(',') as List
        reports_list_abs = reports_list.collect { it -> projectDir / it }
        reports_ch = Channel.of(reports_list_abs).map { ["sample", it] }
    }
    reports_ch.view()
    summary(reports_ch)
}

workflow summary {
    take:
    reports_list

    main:
    summary_json(reports_list)

    emit:
    main_report = summary_json.out.main_report
}

process summary_json {
    publishDir "${params.publish_dir}", enabled: params.publish_dir != "", mode: "copy", saveAs: { filename -> sample_name + "_" + filename }
    cpus 1
    memory '0.5 GB'
    container {
        params.test_container_myco_summary == "" ? params.container_prefix + '/gpas/summary_pipeline:62d0928' : params.test_container_myco_summary
    }

    pod label: "name", value: "summary_pipeline:summary_json"
    pod label: "sample_id", value: "${params.sample_id}"
    pod label: "run_id", value: "${params.run_id}"

    input:
    tuple val(sample_name), path (reports)

    output:
    tuple val(sample_name), path ("main_report.json"), emit: main_report

    script:
    """
    summary_json --reports ${reports} --output main_report.json
    """
}
