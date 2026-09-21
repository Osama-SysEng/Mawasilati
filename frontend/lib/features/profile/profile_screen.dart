import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    if (!auth.isAuthenticated) {
      return AppScaffold(
        title: 'الملف الشخصي',
        children: [
          const ListTile(title: Text('سجّل الدخول لعرض ملفك الشخصي')),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pushNamed('/login'),
            child: const Text('تسجيل الدخول'),
          ),
        ],
      );
    }

    const roleLabels = {
      'passenger': 'راكب',
      'driver': 'سائق',
      'admin': 'إدارة',
    };

    return AppScaffold(
      title: 'الملف الشخصي',
      children: [
        CircleAvatar(
          radius: 40,
          child: Text(
            (auth.name?.isNotEmpty ?? false) ? auth.name![0] : '؟',
            style: const TextStyle(fontSize: 28),
          ),
        ),
        const SizedBox(height: 16),
        ListTile(title: const Text('الاسم'), subtitle: Text(auth.name ?? '-')),
        ListTile(title: const Text('رقم الهاتف'), subtitle: Text(auth.phone ?? '-')),
        ListTile(title: const Text('الدور'), subtitle: Text(roleLabels[auth.role] ?? auth.role ?? '-')),
        ListTile(
          title: const Text('رصيد المحفظة'),
          subtitle: Text('${auth.user?['wallet_balance'] ?? 0} جنيه'),
        ),
        const SizedBox(height: 24),
        ElevatedButton(
          onPressed: () => Navigator.of(context).pushNamed('/settings'),
          child: const Text('الإعدادات'),
        ),
        const SizedBox(height: 12),
        OutlinedButton(
          onPressed: () async {
            await context.read<AuthProvider>().signOut();
            if (context.mounted) {
              Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);
            }
          },
          child: const Text('تسجيل الخروج'),
        ),
      ],
    );
  }
}
