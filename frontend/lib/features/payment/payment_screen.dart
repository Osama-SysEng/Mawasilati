import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/services/api_service.dart';
import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';

class PaymentScreen extends StatefulWidget {
  const PaymentScreen({super.key, this.tripId, this.amount});

  final String? tripId;
  final double? amount;

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  String _method = 'wallet';
  bool _isProcessing = false;
  String? _statusMessage;

  Future<void> _pay() async {
    final auth = context.read<AuthProvider>();
    if (!auth.isAuthenticated) {
      Navigator.of(context).pushNamed('/login');
      return;
    }
    if (widget.tripId == null || widget.amount == null) {
      setState(() => _statusMessage = 'لا توجد رحلة محددة للدفع. احجز رحلة أولاً.');
      return;
    }

    setState(() {
      _isProcessing = true;
      _statusMessage = null;
    });

    try {
      final api = const ApiService().withToken(auth.token);
      final initiated = await api.initiatePayment({
        'trip_id': widget.tripId,
        'method': _method,
        'amount': widget.amount,
      });
      final confirmed = await api.confirmPayment(initiated['payment_id'].toString());
      setState(() {
        _statusMessage = 'تم الدفع بنجاح. رقم التذكرة: ${confirmed['qr_ticket']}';
      });
    } on ApiException catch (e) {
      setState(() => _statusMessage = 'فشل الدفع: ${e.message}');
    } finally {
      if (mounted) {
        setState(() => _isProcessing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'الدفع',
      children: [
        RadioListTile<String>(
          title: const Text('InstaPay'),
          subtitle: const Text('تحويل فوري (تجريبي — يتطلب مفتاح InstaPay الحقيقي)'),
          value: 'instapay',
          groupValue: _method,
          onChanged: (value) => setState(() => _method = value!),
        ),
        RadioListTile<String>(
          title: const Text('Visa / Mastercard'),
          subtitle: const Text('بطاقات بنكية (تجريبي — يتطلب مفتاح بوابة دفع حقيقي)'),
          value: 'visa',
          groupValue: _method,
          onChanged: (value) => setState(() => _method = value!),
        ),
        RadioListTile<String>(
          title: const Text('Wallet'),
          subtitle: const Text('محفظة داخل التطبيق'),
          value: 'wallet',
          groupValue: _method,
          onChanged: (value) => setState(() => _method = value!),
        ),
        const SizedBox(height: 20),
        if (_statusMessage != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(_statusMessage!),
          ),
        ElevatedButton(
          onPressed: _isProcessing ? null : _pay,
          child: Text(_isProcessing ? 'جاري الدفع...' : 'ادفع الآن'),
        ),
      ],
    );
  }
}
