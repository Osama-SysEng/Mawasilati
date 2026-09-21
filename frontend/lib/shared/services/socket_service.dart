import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../core/constants/app_constants.dart';

/// Connects to the backend's `/ws/trip/{tripId}` endpoint for live trip
/// tracking. Drivers send location updates; passengers listen for them.
class SocketService {
  SocketService();

  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>>? _controller;

  Stream<Map<String, dynamic>> connect({
    required String tripId,
    required String role,
    required String? token,
  }) {
    disconnect();

    // The backend authenticates the WebSocket handshake with this JWT (same
    // token used for REST calls) and rejects connections without it.
    final uri = Uri.parse('${AppConstants.wsBaseUrl}/trip/$tripId?role=$role&token=${token ?? ''}');
    final channel = WebSocketChannel.connect(uri);
    final controller = StreamController<Map<String, dynamic>>.broadcast();

    channel.stream.listen(
      (raw) {
        try {
          final decoded = jsonDecode(raw as String);
          if (decoded is Map<String, dynamic>) {
            controller.add(decoded);
          }
        } catch (_) {
          // Ignore malformed frames instead of crashing the stream.
        }
      },
      onError: controller.addError,
      onDone: controller.close,
    );

    _channel = channel;
    _controller = controller;
    return controller.stream;
  }

  /// Drivers call this to push their current location to any listening
  /// passenger connected to the same trip.
  void sendLocation({required double latitude, required double longitude}) {
    _channel?.sink.add(jsonEncode({'latitude': latitude, 'longitude': longitude}));
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
    unawaited(_controller?.close());
    _controller = null;
  }
}
