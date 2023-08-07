#!/usr/bin/env nextflow

//Set DSL2 syntax
nextflow.enable.dsl = 2

//Define ANSI colours for ease
ANSI_GREEN = "\033[1;32m"
ANSI_RESET = "\033[0m"

params.help = ''

process summary_json {
    cpus 1
    memory '0.5 GB'
    container 'lhr.ocir.io/lrbvkel2wjot/gpas/summary_pipeline:latest'

  input:
    path gatekeeper
    path mapping
    path mykrobe
    path gnomonicus

  output:
    path "main_report.json", emit: main_report
    path "main_error.json", emit: main_error

  script:
    def gatekeeper_param = gatekeeper.name != '/EMPTY' ? "--gatekeeper $gatekeeper" : ''
    def mapping_param = mapping.name != '/EMPTY' ? "--mapping $mapping" : ''
    def mykrobe_param = mykrobe.name != '/EMPTY' ? "--mykrobe $mykrobe" : ''
    def gnomonicus_param = gnomonicus.name != '/EMPTY' ? "--gnomonicus $gnomonicus" : ''
    """
    summary_json ${gatekeeper_param} ${mapping_param} ${mykrobe_param} ${gnomonicus_param} --output main_report.json
    touch main_error.json
    """
}

workflow summary {
  take:
    gatekeeper_report_path
    mapping_report_path
    mykrobe_report_path
    gnomonicus_report_path

  main:
    if (params.gatekeeper_report_path == '') {
    exit 1, 'error: --gatekeeper_report_path is mandatory'
    }

    if (params.help) {
    log.info '''
            ========================================================================
            Summary

            Combines output from workflow steps to create a single summary JSON file.

            Parameters:
            ------------------------------------------------------------------------
            --gatekeeper_report_path  Path to gatekeeper report (`gatekeeper_report.json`).
            --mapping_report_path  Path to competitive mapping report (`competitivemapping_report.json`).
            --mykrobe_report_path  Path to mykrobe report (`mykrobe_report.json`).
            --gnomonicus_report_path  Path to gnomonicus report (`gnomonicus.json`).
            '''

            .stripIndent()

    exit(0)
    }

  log.info """
        ========================================================================
        Summary

        Combines output from workflow steps to create a single summary JSON file.

        Parameters:
        ------------------------------------------------------------------------

        --gatekeeper_report_path    $params.gatekeeper_report_path
        --mapping_report_path       $params.mapping_report_path
        --mykrobe_report_path       $params.mykrobe_report_path
        --gnomonicus_report_path    $params.gnomonicus_report_path

        Runtime data:
        ------------------------------------------------------------------------

        Running with profile  ${ANSI_GREEN}${workflow.profile}${ANSI_RESET}
        Running as user       ${ANSI_GREEN}${workflow.userName}${ANSI_RESET}
        Launch directory      ${ANSI_GREEN}${workflow.launchDir}${ANSI_RESET}
        Project directory     ${ANSI_GREEN}${projectDir}${ANSI_RESET}
        """
        .stripIndent()

    summary_json_output = summary_json(gatekeeper_report_path, 
                                       mapping_report_path, 
                                       mykrobe_report_path, 
                                       gnomonicus_report_path)

  emit:
    main_report = summary_json_output.main_report
    error_report = summary_json_output.main_error
}

workflow {
  main:
    gatekeeper_report = params.gatekeeper_report_path
                          ? Channel.fromPath(params.gatekeeper_report_path, checkIfExists:true)
                          : Channel.empty()
    mapping_report = params.mapping_report_path
                          ? Channel.fromPath(params.mapping_report_path, checkIfExists:true)
                          : Channel.empty()
    mykrobe_report = params.mykrobe_report_path
                          ? Channel.fromPath(params.mykrobe_report_path, checkIfExists:true)
                          : Channel.empty()
    gnomonicus_report = params.gnomonicus_report_path
                          ? Channel.fromPath(params.gnomonicus_report_path, checkIfExists:true)
                          : Channel.empty()
    summary(gatekeeper_report, 
            mapping_report.ifEmpty('/EMPTY'), 
            mykrobe_report.ifEmpty('/EMPTY'), 
            gnomonicus_report.ifEmpty('/EMPTY'))
}