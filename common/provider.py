"""
Base class for all providers
"""

import abc

class Provider(abc.ABC):
    @abc.abstractmethod
    def authorize(self):
        pass

    @abc.abstractmethod
    def upload(self, filename):
        pass

    @abc.abstractmethod
    def retrieve(self, filename):
        """
        Fetch the specified filename from the API
        :param filename: 
        :return: 
        """
        pass
