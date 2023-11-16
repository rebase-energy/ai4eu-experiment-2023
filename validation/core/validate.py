import great_expectations as gx
import tempfile



def validate(df, expectations):
    context = gx.get_context()

    # Somehow creating a validator directly from in-memory dataframe
    # causes a problem, so I'm just dumping it temporarily and read it again
    with tempfile.TemporaryDirectory() as tmpdirname:
        file_name = f"{tmpdirname}/temp.csv"
        df.to_csv(file_name, index=False)
        validator = context.sources.pandas_default.read_csv(
            file_name
        )

    for exp in expectations:
        getattr(validator, exp['expectation'])(*exp['args'])

    # Validate data
    checkpoint = gx.checkpoint.SimpleCheckpoint(
        name="checkpoint",
        data_context=context,
        validator=validator,
    )

    checkpoint_result = checkpoint.run()

    return checkpoint_result
