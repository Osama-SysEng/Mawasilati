import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/utils/formatters.dart';
import '../../shared/services/api_service.dart';
import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';

class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen> {
  Future<Map<String, dynamic>>? _historyFuture;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final auth = context.read<AuthProvider>();
    if (auth.isAuthenticated && _historyFuture == null) {
      _historyFuture = const ApiService().withToken(auth.token).paymentHistory();
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final balance = (auth.user?['wallet_balance'] as num?) ?? 0;

    if (!auth.isAuthenticated) {
      return AppScaffold(
        title: 'المحفظة',
        children: [
          const ListTile(title: Text('سجّل الدخول لعرض محفظتك')),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pushNamed('/login'),
            child: const Text('تسجيل الدخول'),
          ),
        ],
      );
    }

    return AppScaffold(
      title: 'المحفظة',
      children: [
        ListTile(title: const Text('الرصيد'), subtitle: Text(AppFormatters.currency(balance))),
        const SizedBox(height: 12),
        const ElevatedButton(
          onPressed: null,
          child: Text('شحن المحفظة (يتطلب بوابة دفع حقيقية)'),
        ),
        const Divider(height: 32),
        const Text('سجل المدفوعات', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        FutureBuilder<Map<String, dynamic>>(
          future: _historyFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Padding(
                padding: EdgeInsets.symmetric(vertical: 16),
                child: Center(child: CircularProgressIndicator()),
              );
            }
            final items = (snapshot.data?['items'] as List?) ?? [];
            if (items.isEmpty) {
              return const Padding(
                padding: EdgeInsets.only(top: 12),
                child: Text('لا توجد مدفوعات بعد'),
              );
            }
            return Column(
              children: items.map((raw) {
                final payment = Map<String, dynamic>.from(raw as Map);
                return ListTile(
                  title: Text('${payment['method']} — ${payment['status']}'),
                  subtitle: Text(AppFormatters.currency((payment['amount'] as num?) ?? 0)),
                );
              }).toList(),
            );
          },
        ),
      ],
    );
  }
}
