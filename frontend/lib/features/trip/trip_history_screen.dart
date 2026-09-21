import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/services/api_service.dart';
import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';

class TripHistoryScreen extends StatefulWidget {
  const TripHistoryScreen({super.key});

  @override
  State<TripHistoryScreen> createState() => _TripHistoryScreenState();
}

class _TripHistoryScreenState extends State<TripHistoryScreen> {
  Future<Map<String, dynamic>>? _historyFuture;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final auth = context.read<AuthProvider>();
    if (auth.isAuthenticated && _historyFuture == null) {
      _historyFuture = const ApiService().withToken(auth.token).tripHistory();
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    if (!auth.isAuthenticated) {
      return AppScaffold(
        title: 'سجل الرحلات',
        children: [
          const ListTile(title: Text('سجّل الدخول لعرض رحلاتك')),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pushNamed('/login'),
            child: const Text('تسجيل الدخول'),
          ),
        ],
      );
    }

    return AppScaffold(
      title: 'سجل الرحلات',
      children: [
        FutureBuilder<Map<String, dynamic>>(
          future: _historyFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: Center(child: CircularProgressIndicator()),
              );
            }
            if (snapshot.hasError) {
              return Text('تعذر تحميل السجل: ${snapshot.error}', style: const TextStyle(color: Colors.red));
            }
            final items = (snapshot.data?['items'] as List?) ?? [];
            if (items.isEmpty) {
              return const ListTile(
                title: Text('لا توجد رحلات بعد'),
                subtitle: Text('ابدأ أول رحلة لك من الصفحة الرئيسية'),
              );
            }
            return Column(
              children: items.map((raw) {
                final trip = Map<String, dynamic>.from(raw as Map);
                final route = trip['transport_mix'];
                final routeText = route is List ? route.join(' → ') : route.toString();
                return Card(
                  child: ListTile(
                    title: Text('الحالة: ${trip['status']}'),
                    subtitle: Text('$routeText\n${trip['total_price']} جنيه'),
                    isThreeLine: true,
                  ),
                );
              }).toList(),
            );
          },
        ),
      ],
    );
  }
}
