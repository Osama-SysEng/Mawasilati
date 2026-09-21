import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/services/api_service.dart';
import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';
import 'trip_tracking_screen.dart';

class TripOptionsScreen extends StatefulWidget {
  const TripOptionsScreen({super.key, this.planResult = const {}, this.planRequest = const {}});

  final Map<String, dynamic> planResult;
  final Map<String, dynamic> planRequest;

  @override
  State<TripOptionsScreen> createState() => _TripOptionsScreenState();
}

class _TripOptionsScreenState extends State<TripOptionsScreen> {
  String? _bookingOptionId;
  String? _error;

  List<Map<String, dynamic>> get _options {
    final raw = widget.planResult['options'];
    if (raw is List) {
      return raw.whereType<Map>().map((item) => Map<String, dynamic>.from(item)).toList();
    }
    return [];
  }

  Future<void> _book(Map<String, dynamic> option) async {
    final auth = context.read<AuthProvider>();
    if (!auth.isAuthenticated) {
      Navigator.of(context).pushNamed('/login');
      return;
    }

    setState(() {
      _bookingOptionId = option['id']?.toString();
      _error = null;
    });

    try {
      final result = await const ApiService().withToken(auth.token).bookTrip(option: option);
      if (!mounted) return;
      final tripId = result['trip_id']?.toString();
      await showDialog<void>(
        context: context,
        builder: (context) {
          return AlertDialog(
            title: const Text('تم تأكيد الحجز'),
            content: Text('Trip ID: $tripId'),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('حسناً'),
              ),
            ],
          );
        },
      );
      if (!mounted || tripId == null) return;
      await Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => TripTrackingScreen(tripId: tripId)),
      );
    } on ApiException catch (e) {
      setState(() {
        _error = e.message;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() {
          _bookingOptionId = null;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'خيارات الرحلة',
      children: [
        Card(
          child: ListTile(
            title: Text('من: ${widget.planRequest['origin_label'] ?? '-'}'),
            subtitle: Text('إلى: ${widget.planRequest['destination_label'] ?? '-'}'),
          ),
        ),
        const SizedBox(height: 12),
        if (widget.planResult['parsed_intent'] != null)
          Card(
            child: ListTile(
              title: const Text('النية المفهومة'),
              subtitle: Text(widget.planResult['parsed_intent'].toString()),
            ),
          ),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.only(top: 8, bottom: 12),
            child: Text(
              _error!,
              style: const TextStyle(color: Colors.red),
            ),
          ),
        const SizedBox(height: 12),
        ..._options.map((option) {
          final id = option['id']?.toString();
          final route = option['route'];
          final routeText = route is List ? route.join(' → ') : route.toString();
          final isBooking = _bookingOptionId == id;
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      option['type']?.toString() ?? 'خيار',
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text('المسار: $routeText'),
                    Text('السعر: ${option['price']} جنيه'),
                    Text('الوقت: ${option['time']}'),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: isBooking ? null : () => _book(option),
                      child: Text(isBooking ? 'جاري الحجز...' : 'احجز'),
                    ),
                  ],
                ),
              ),
            ),
          );
        }),
        if (_options.isEmpty)
          const Padding(
            padding: EdgeInsets.only(top: 12),
            child: Text('لا توجد خيارات حالياً.'),
          ),
      ],
    );
  }
}
