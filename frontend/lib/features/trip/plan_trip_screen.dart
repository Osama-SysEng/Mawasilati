import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/services/api_service.dart';
import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';
import 'trip_options_screen.dart';

class PlanTripScreen extends StatefulWidget {
  const PlanTripScreen({super.key});

  @override
  State<PlanTripScreen> createState() => _PlanTripScreenState();
}

class _PlanTripScreenState extends State<PlanTripScreen> {
  final TextEditingController _originController = TextEditingController();
  final TextEditingController _destinationController = TextEditingController();
  final TextEditingController _budgetController = TextEditingController();
  bool _isLoading = false;
  String? _error;

  @override
  void dispose() {
    _originController.dispose();
    _destinationController.dispose();
    _budgetController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final auth = context.read<AuthProvider>();
    if (!auth.isAuthenticated) {
      Navigator.of(context).pushNamed('/login');
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    final payload = <String, dynamic>{
      'origin_label': _originController.text.trim(),
      'destination_label': _destinationController.text.trim(),
      if (_budgetController.text.trim().isNotEmpty)
        'budget': double.tryParse(_budgetController.text.trim()),
    }..removeWhere((key, value) => value == null || value == '');

    try {
      final result = await const ApiService().withToken(auth.token).planTrip(payload);
      if (!mounted) return;
      await Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => TripOptionsScreen(
            planResult: result,
            planRequest: payload,
          ),
        ),
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
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'تخطيط رحلة',
      children: [
        TextField(
          controller: _originController,
          decoration: const InputDecoration(labelText: 'من'),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _destinationController,
          decoration: const InputDecoration(labelText: 'إلى'),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _budgetController,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(labelText: 'الميزانية بالجنيه'),
        ),
        const SizedBox(height: 20),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(
              _error!,
              style: const TextStyle(color: Colors.red),
            ),
          ),
        ElevatedButton(
          onPressed: _isLoading ? null : _submit,
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 14),
            child: Text(_isLoading ? 'جاري الحساب...' : 'احسب الخيارات'),
          ),
        ),
      ],
    );
  }
}
