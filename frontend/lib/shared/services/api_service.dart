import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../core/constants/app_constants.dart';

class ApiException implements Exception {
  ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  bool get isUnauthorized => statusCode == 401;

  @override
  String toString() {
    if (statusCode == null) {
      return message;
    }
    return 'ApiException($statusCode): $message';
  }
}

class ApiService {
  const ApiService({this.baseUrl = AppConstants.apiBaseUrl, this.authToken});

  final String baseUrl;

  /// Pass the current JWT (from `AuthProvider.token`) so protected endpoints
  /// (trip, payment, driver, ai, /auth/me) authenticate correctly.
  final String? authToken;

  ApiService withToken(String? token) => ApiService(baseUrl: baseUrl, authToken: token);

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  Future<Map<String, dynamic>> _request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? queryParameters,
  }) async {
    late final http.Response response;
    final headers = {
      'Content-Type': 'application/json',
      if (authToken != null) 'Authorization': 'Bearer $authToken',
    };
    final uri = _uri(path).replace(queryParameters: queryParameters);

    if (method == 'GET') {
      response = await http.get(uri, headers: headers);
    } else if (method == 'POST') {
      response = await http.post(uri, headers: headers, body: body == null ? null : jsonEncode(body));
    } else {
      throw UnsupportedError('Unsupported method: $method');
    }

    final decoded = _decodeJson(response.body);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      final detail = decoded['detail']?.toString() ?? decoded['message']?.toString() ?? response.body;
      throw ApiException(detail, statusCode: response.statusCode);
    }
    return decoded;
  }

  Future<Map<String, dynamic>> getHealth() {
    return _request('GET', '/health');
  }

  Future<Map<String, dynamic>> register({
    required String name,
    required String phone,
    required String password,
    String role = 'passenger',
  }) {
    return _request(
      'POST',
      '/auth/register',
      body: {
        'name': name,
        'phone': phone,
        'password': password,
        'role': role,
      },
    );
  }

  Future<Map<String, dynamic>> login({required String phone, required String password}) {
    return _request(
      'POST',
      '/auth/login',
      body: {'phone': phone, 'password': password},
    );
  }

  Future<Map<String, dynamic>> me() {
    return _request('GET', '/auth/me');
  }

  Future<Map<String, dynamic>> parseTrip(String text) {
    return _request(
      'POST',
      '/ai/parse-trip',
      body: {'text': text},
    );
  }

  Future<Map<String, dynamic>> chat(String message) {
    return _request(
      'POST',
      '/ai/chat',
      body: {'message': message},
    );
  }

  Future<Map<String, dynamic>> planTrip(Map<String, dynamic> payload) {
    return _request(
      'POST',
      '/trip/plan',
      body: payload,
    );
  }

  Future<Map<String, dynamic>> getTripOptions({
    double? originLat,
    double? originLng,
    double? destLat,
    double? destLng,
    double? budget,
  }) {
    final query = <String, String>{
      if (originLat != null) 'origin_lat': originLat.toString(),
      if (originLng != null) 'origin_lng': originLng.toString(),
      if (destLat != null) 'dest_lat': destLat.toString(),
      if (destLng != null) 'dest_lng': destLng.toString(),
      if (budget != null) 'budget': budget.toString(),
    };
    return _request('GET', '/trip/options', queryParameters: query);
  }

  Future<Map<String, dynamic>> bookTrip({required Map<String, dynamic> option}) {
    return _request(
      'POST',
      '/trip/book',
      body: {'option': option},
    );
  }

  Future<Map<String, dynamic>> tripHistory() {
    return _request('GET', '/trip/history');
  }

  Future<Map<String, dynamic>> trackTrip(String tripId) {
    return _request('GET', '/trip/track/$tripId');
  }

  Future<Map<String, dynamic>> initiatePayment(Map<String, dynamic> payload) {
    return _request(
      'POST',
      '/payment/initiate',
      body: payload,
    );
  }

  Future<Map<String, dynamic>> confirmPayment(String paymentId) {
    return _request(
      'POST',
      '/payment/confirm',
      body: {'payment_id': paymentId},
    );
  }

  Future<Map<String, dynamic>> paymentHistory() {
    return _request('GET', '/payment/history');
  }

  Future<Map<String, dynamic>> getHeatmap({double radiusKm = 5.0}) {
    return _request('GET', '/driver/heatmap', queryParameters: {'radius_km': radiusKm.toString()});
  }

  Future<Map<String, dynamic>> updateDriverLocation({
    required double latitude,
    required double longitude,
    String? tripId,
  }) {
    // driver_id is never sent — the backend derives it from the auth token.
    return _request(
      'POST',
      '/driver/location',
      body: {
        'latitude': latitude,
        'longitude': longitude,
        if (tripId != null) 'trip_id': tripId,
      },
    );
  }

  Map<String, dynamic> _decodeJson(String body) {
    if (body.isEmpty) {
      return {};
    }
    final decoded = jsonDecode(body);
    if (decoded is Map<String, dynamic>) {
      return decoded;
    }
    return {'data': decoded};
  }
}
