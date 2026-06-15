def extract_text_from_response(
    response
):

    messages = response.get(
        "messages",
        []
    )

    if not messages:
        return "Sem resposta."

    content = messages[-1].content

    if isinstance(
        content,
        str
    ):
        return content

    if isinstance(
        content,
        list
    ):

        texts = []

        for item in content:

            if isinstance(item, dict):

                text = item.get(
                    "text"
                )

                if text:
                    texts.append(text)

        return "\n".join(texts)

    return str(content)