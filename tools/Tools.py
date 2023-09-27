class Tools:

    @classmethod
    def get_dir_path(cls, abs_file_path):
        return abs_file_path[:abs_file_path.rfind("/")+1]
