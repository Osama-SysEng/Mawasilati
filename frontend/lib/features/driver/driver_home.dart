import 'dart:async';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/services/api_service.dart';
import '../../shared/services/location_service.dart';
import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';

class DriverHomeScreen extends StatefulWidget {
  const DriverHomeScreen({super.key});

  @override
  State<DriverHomeScreen> createState() => _DriverHomeScreenState();
}

class _DriverHomeScreenState extends State<DriverHomeScreen> {
  final LocationService _locationService = const LocationService();
  final TextEditingController _tripIdController = TextEditingController();
  StreamSubscription<Map<String, double>>? _positionSubscription;
  bool _isSharingLocation = false;
  String _statusText = 'مشاركة الموقع متوقفة';
  Map<String, double>? _lastLocation;

  Future<void> _toggleSharing() async {
    final auth = context.read<AuthProvider>();
    if (!auth.isAuthenticated || auth.userId == null) {
      Navigator.of(context).pushNamed('/login');
      return;
    }

    if (_isSharingLocation) {
      await _positionSubscription?.cancel();
      _positionSubscription = null;
      setState(() {
        _isSharingLocation = false;
        _statusText = 'مشاركة الموقع متوقفة';
      });
      return;
    }

    final hasPermission = await _locationService.ensurePermission();
    if (!hasPermission) {
      setState(() => _statusText = 'يجب السماح بالوصول للموقع لمشاركته مع الركاب');
      return;
    }

    setState(() {
      _isSharingLocation = true;
      _statusText = 'جاري مشاركة الموقع...';
    });

    final api = const ApiService().withToken(auth.token);
    final tripId = _tripIdController.text.trim();

    _positionSubscription = _locationService.watchPosition().listen((location) async {
      if (!mounted) return;
      setState(() {
        _lastLocation = location;
        _statusText = 'يتم إرسال الموقع الآن';
      });
      try {
        // The backend derives the driver identity from the auth token, and
        // relays this update to the trip's live tracking room if a trip id
        // is supplied, so the passenger's tracking screen updates in real time.
        await api.updateDriverLocation(
          latitude: location['latitude']!,
          longitude: location['longitude']!,
          tripId: tripId.isEmpty ? null : tripId,
        );
      } on ApiException {
        // Keep sharing even if a single update fails; the next tick retries.
      }
    });

    final current = await _locationService.currentLocation();
    if (!mounted) return;
    setState(() => _lastLocation = current);
  }

  @override
  void dispose() {
    _positionSubscription?.cancel();
    _tripIdController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'لوحة السائق',
      children: [
        const ListTile(title: Text('الطلبات القريبة'), subtitle: Text('3 طلبات متاحة')),
        const ListTile(title: Text('حالة الخرائط الحرارية'), subtitle: Text('محدثة كل 90 ثانية')),
        const Divider(height: 32),
        TextField(
          controller: _tripIdController,
          enabled: !_isSharingLocation,
          decoration: const InputDecoration(
            labelText: 'رقم الرحلة النشطة (اختياري)',
            helperText: 'أدخله ليتابع الراكب موقعك مباشرة على شاشة تتبع الرحلة',
          ),
        ),
        const SizedBox(height: 8),
        ListTile(
          title: const Text('مشاركة الموقع مباشرة'),
          subtitle: Text(_statusText),
          trailing: Switch(value: _isSharingLocation, onChanged: (_) => _toggleSharing()),
        ),
        if (_lastLocation != null)
          ListTile(
            title: const Text('آخر موقع مُرسل'),
            subtitle: Text('${_lastLocation!['latitude']}, ${_lastLocation!['longitude']}'),
          ),
      ],
    );
  }
}
