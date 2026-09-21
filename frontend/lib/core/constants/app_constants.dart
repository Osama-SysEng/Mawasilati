class AppConstants {
  /// Base URL for the versioned REST API.
  static const String apiBaseUrl = 'http://localhost:8000/api/v1';

  /// Base URL for the trip-tracking WebSocket, e.g. `ws://localhost:8000/ws`.
  /// Connect to `$wsBaseUrl/trip/{tripId}?role=driver|passenger`.
  static const String wsBaseUrl = 'ws://localhost:8000/ws';
}
