# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from validation import model_pb2 as validation_dot_model__pb2


class RebaseValidationStub(object):
    """Define the service
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Validate = channel.unary_unary(
                '/RebaseValidation/Validate',
                request_serializer=validation_dot_model__pb2.Input.SerializeToString,
                response_deserializer=validation_dot_model__pb2.Result.FromString,
                )


class RebaseValidationServicer(object):
    """Define the service
    """

    def Validate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RebaseValidationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Validate': grpc.unary_unary_rpc_method_handler(
                    servicer.Validate,
                    request_deserializer=validation_dot_model__pb2.Input.FromString,
                    response_serializer=validation_dot_model__pb2.Result.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'RebaseValidation', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RebaseValidation(object):
    """Define the service
    """

    @staticmethod
    def Validate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RebaseValidation/Validate',
            validation_dot_model__pb2.Input.SerializeToString,
            validation_dot_model__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
