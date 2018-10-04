import fire


class Run(object):

    @staticmethod
    def clear_cache():
        from qgenda.cache import cache
        cache.clear()


if __name__ == '__main__':
  fire.Fire(Run)
