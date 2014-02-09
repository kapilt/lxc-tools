
from zope.interface import Interface


class ILayerPart(Interface):

    def download():
        """
        """


class ILayer(Interface):

    def get_uuid():
        """Get guid for layer.
        """

    def get_signature():
        """Return bytes of GPG Signature
        """

    def get_parts():
        """Return url parts of layers.
        """


class Image(Interface):

    def get_layers():
        """
        """


class LayerRepository(Interface):

    def get_layer(uuid):
        pass

    def get_layers(uuid_iter):
        pass


class ImageRepository(Interface):

    def search(query_terms):
        """
        """
