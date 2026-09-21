import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/constants/app_constants.dart';
import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _notificationsEnabled = true;
  bool _shareLiveLocation = true;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    return AppScaffold(
      title: 'الإعدادات',
      children: [
        SwitchListTile(
          title: const Text('تفعيل الإشعارات'),
          subtitle: const Text('يتطلب إعداد Firebase (غير مفعّل بعد في هذا السكافولد)'),
          value: _notificationsEnabled,
          onChanged: (value) => setState(() => _notificationsEnabled = value),
        ),
        SwitchListTile(
          title: const Text('مشاركة الموقع أثناء الرحلة'),
          subtitle: const Text('يُستخدم لتتبع رحلتك مباشرة على الخريطة'),
          value: _shareLiveLocation,
          onChanged: (value) => setState(() => _shareLiveLocation = value),
        ),
        const Divider(height: 32),
        ListTile(title: const Text('عنوان الخادم'), subtitle: Text(AppConstants.apiBaseUrl)),
        const SizedBox(height: 24),
        if (auth.isAuthenticated)
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
