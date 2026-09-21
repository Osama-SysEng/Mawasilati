import 'package:geolocator/geolocator.dart';

/// Wraps `geolocator` with the permission dance the app needs before it can
/// read or stream the device's GPS position.
class LocationService {
  const LocationService();

  Future<bool> ensurePermission() async {
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.deniedForever) {
      return false;
    }
    if (!await Geolocator.isLocationServiceEnabled()) {
      return false;
    }
    return permission == LocationPermission.always || permission == LocationPermission.whileInUse;
  }

  Future<Map<String, double>> currentLocation() async {
    final hasPermission = await ensurePermission();
    if (!hasPermission) {
      // Falls back to central Cairo so the UI still has something to show
      // when location access is unavailable (simulator, denied permission).
      return {'latitude': 30.0444, 'longitude': 31.2357};
    }
    final position = await Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(accuracy: LocationAccuracy.high),
    );
    return {'latitude': position.latitude, 'longitude': position.longitude};
  }

  /// Streams position updates, e.g. for a driver broadcasting live location.
  Stream<Map<String, double>> watchPosition({int distanceFilterMeters = 20}) {
    return Geolocator.getPositionStream(
      locationSettings: LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: distanceFilterMeters,
      ),
    ).map((position) => {'latitude': position.latitude, 'longitude': position.longitude});
  }
}
