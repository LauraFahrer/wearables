if (params.workflow == 'data_accession') {

    workflow DATA_ACCESSION {
        // Module für data_accession
    }

    DATA_ACCESSION()

} else if (params.workflow == 'data_processing') {

    workflow DATA_PROCESSING {
        // Module für data_processing
    }

    DATA_PROCESSING()

} else if (params.workflow == 'model_tuning') {


    workflow MODEL_TUNING {
        // Module für model_tuning
    }

    MODEL_TUNING()

} else if (params.workflow == 'model_evaluation') {

    workflow MODEL_EVALUATION {
        // Module für model_evaluation
    }

    MODEL_EVALUATION()

} else {
    
    error "Unknown workflow: ${params.workflow}. Available workflows: data_accession, data_processing"
}