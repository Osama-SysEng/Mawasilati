import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/services/api_service.dart';
import '../../shared/services/session.dart';
import '../../shared/services/socket_service.dart';
import '../../shared/widgets/app_scaffold.dart';

class TripTrackingScreen extends StatefulWidget {
  const TripTrackingScreen({super.key, this.tripId});

  final String? tripId;

  @override
  State<TripTrackingScreen> createState() => _TripTrackingScreenState();
}

class _TripTrackingScreenState extends State<TripTrackingScreen> {
  final SocketService _socketService = SocketService();
  Map<String, dynamic>? _trip;
  double? _liveLat;
  double? _liveLng;
  String _connectionStatus = 'غير متصل';

  @override
  void initState() {
    super.initState();
    if (widget.tripId != null) {
      _loadTrip(widget.tripId!);
      _connect(widget.tripId!);
    }
  }

  Future<void> _loadTrip(String tripId) async {
    try {
      final token = context.read<AuthProvider>().token;
      final result = await const ApiService().withToken(token).trackTrip(tripId);
      if (!mounted) return;
      setState(() {
        _trip = result;
      });
    } catch (_) {
      // Keep showing placeholder state if the trip lookup fails.
    }
  }

  void _connect(String tripId) {
    setState(() {
      _connectionStatus = 'جاري الاتصال...';
    });
    final token = context.read<AuthProvider>().token;
    _socketService.connect(tripId: tripId, role: 'passenger', token: token).listen(
      (message) {
        if (message['type'] == 'location' && mounted) {
          setState(() {
            _liveLat = (message['latitude'] as num?)?.toDouble();
            _liveLng = (message['longitude'] as num?)?.toDouble();
            _connectionStatus = 'متصل - يتم استقبال الموقع مباشرة';
          });
        }
      },
      onError: (_) {
        if (mounted) {
          setState(() => _connectionStatus = 'تعذر الاتصال بخدمة التتبع المباشر');
        }
      },
    );
  }

  @override
  void dispose() {
    _socketService.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final status = _trip?['status']?.toString() ?? (widget.tripId == null ? '-' : 'جاري التحميل...');
    final liveLocationText = _liveLat != null && _liveLng != null
        ? '${_liveLat!.toStringAsFixed(5)}, ${_liveLng!.toStringAsFixed(5)}'
        : 'بانتظار موقع السائق';

    return AppScaffold(
      title: 'تتبع الرحلة',
      children: [
        if (widget.tripId == null)
          const Padding(
            padding: EdgeInsets.only(bottom: 12),
            child: Text('لا توجد رحلة نشطة لعرضها بعد. احجز رحلة أولاً من صفحة خيارات الرحلة.'),
          ),
        ListTile(title: const Text('الحالة'), subtitle: Text(status)),
        ListTile(title: const Text('الموقع الحالي (مباشر)'), subtitle: Text(liveLocationText)),
        ListTile(title: const Text('حالة الاتصال المباشر'), subtitle: Text(_connectionStatus)),
        if (_trip?['total_price'] != null)
          ListTile(title: const Text('السعر الإجمالي'), subtitle: Text('${_trip!['total_price']} جنيه')),
      ],
    );
  }
}
