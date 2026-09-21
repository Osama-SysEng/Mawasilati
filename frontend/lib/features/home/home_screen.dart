import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/services/api_service.dart';
import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = const ApiService();
  late final Future<Map<String, dynamic>> _healthFuture;

  @override
  void initState() {
    super.initState();
    _healthFuture = _apiService.getHealth();
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    return AppScaffold(
      title: 'Mawasilati',
      children: [
        const Text(
          'منصة النقل الذكي الموحدة',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text('احجز، تتبع، وادفع عبر رحلة متعددة الوسائل داخل تطبيق واحد.'),
        const SizedBox(height: 16),
        FutureBuilder<Map<String, dynamic>>(
          future: _healthFuture,
          builder: (context, snapshot) {
            final status = snapshot.connectionState == ConnectionState.done
                ? (snapshot.hasError ? 'Backend unavailable' : 'Backend connected')
                : 'Checking backend...';
            final details = snapshot.hasData ? snapshot.data.toString() : (snapshot.hasError ? snapshot.error.toString() : '');
            return Card(
              child: ListTile(
                leading: const Icon(Icons.cloud_done_outlined),
                title: Text(status),
                subtitle: Text(details),
              ),
            );
          },
        ),
        const SizedBox(height: 12),
        Card(
          child: ListTile(
            leading: Icon(auth.isAuthenticated ? Icons.person : Icons.person_outline),
            title: Text(auth.isAuthenticated ? 'مرحباً ${auth.name ?? ''}' : 'لم تسجّل الدخول بعد'),
            subtitle: Text(auth.isAuthenticated ? auth.phone ?? '' : 'سجّل الدخول لحجز رحلاتك وتتبعها'),
          ),
        ),
        const SizedBox(height: 24),
        if (!auth.isAuthenticated) ...[
          _NavButton(label: 'تسجيل الدخول', route: '/login'),
          _NavButton(label: 'إنشاء حساب', route: '/register'),
        ] else ...[
          _NavButton(label: 'الملف الشخصي', route: '/profile'),
        ],
        _NavButton(label: 'تخطيط رحلة', route: '/plan-trip'),
        _NavButton(label: 'خيارات الرحلة', route: '/trip-options'),
        _NavButton(label: 'تتبع الرحلة', route: '/trip-tracking'),
        _NavButton(label: 'سجل الرحلات', route: '/trip-history'),
        _NavButton(label: 'محادثة AI', route: '/chat'),
        _NavButton(label: 'الدفع', route: '/payment'),
        _NavButton(label: 'المحفظة', route: '/wallet'),
        _NavButton(label: 'لوحة السائق', route: '/driver-home'),
        _NavButton(label: 'Heatmap', route: '/heatmap'),
        _NavButton(label: 'الإعدادات', route: '/settings'),
      ],
    );
  }
}

class _NavButton extends StatelessWidget {
  const _NavButton({required this.label, required this.route});

  final String label;
  final String route;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: ElevatedButton(
        onPressed: () => Navigator.of(context).pushNamed(route),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 14),
          child: Text(label),
        ),
      ),
    );
  }
}
