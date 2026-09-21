import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Holds the signed-in user + JWT and persists the token securely across
/// app restarts. Wrap the app in `ChangeNotifierProvider<AuthProvider>` and
/// call `restore()` once at startup.
class AuthProvider extends ChangeNotifier {
  AuthProvider({FlutterSecureStorage? storage}) : _storage = storage ?? const FlutterSecureStorage();

  static const _tokenKey = 'mawasilati_access_token';

  final FlutterSecureStorage _storage;

  Map<String, dynamic>? _user;
  String? _token;
  bool _isRestoring = true;

  bool get isAuthenticated => _token != null && _user != null;
  bool get isRestoring => _isRestoring;
  Map<String, dynamic>? get user => _user;
  String? get token => _token;

  String? get userId => _user?['id']?.toString();
  String? get name => _user?['name']?.toString();
  String? get phone => _user?['phone']?.toString();
  String? get role => _user?['role']?.toString();

  /// Reads a previously stored token from secure storage. Since the token is
  /// stored without the user profile, callers should refresh `/auth/me`
  /// after this resolves to repopulate `user`.
  Future<String?> restoreToken() async {
    _token = await _storage.read(key: _tokenKey);
    _isRestoring = false;
    notifyListeners();
    return _token;
  }

  Future<void> signIn({required Map<String, dynamic> user, required String token}) async {
    _user = Map<String, dynamic>.from(user);
    _token = token;
    await _storage.write(key: _tokenKey, value: token);
    notifyListeners();
  }

  void setUser(Map<String, dynamic> user) {
    _user = Map<String, dynamic>.from(user);
    notifyListeners();
  }

  Future<void> signOut() async {
    _user = null;
    _token = null;
    await _storage.delete(key: _tokenKey);
    notifyListeners();
  }
}
