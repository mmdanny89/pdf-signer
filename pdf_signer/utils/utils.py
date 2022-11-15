import magic


def get_mimetype_file(file_path):
    mime = magic.Magic(mime=True)
    # "application/pdf"
    return mime.from_file(filename=file_path)
