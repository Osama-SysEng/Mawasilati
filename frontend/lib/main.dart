import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/theme/app_theme.dart';
import 'features/ai_chat/chat_screen.dart';
import 'features/auth/login_screen.dart';
import 'features/auth/register_screen.dart';
import 'features/driver/driver_home.dart';
import 'features/driver/heatmap_screen.dart';
import 'features/home/home_screen.dart';
import 'features/payment/payment_screen.dart';
import 'features/payment/wallet_screen.dart';
import 'features/profile/profile_screen.dart';
import 'features/profile/settings_screen.dart';
import 'features/trip/plan_trip_screen.dart';
import 'features/trip/trip_history_screen.dart';
import 'features/trip/trip_options_screen.dart';
import 'features/trip/trip_tracking_screen.dart';
import 'shared/services/api_service.dart';
import 'shared/services/session.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => AuthProvider(),
      child: const MawasilatiApp(),
    ),
  );
}

class MawasilatiApp extends StatefulWidget {
  const MawasilatiApp({super.key});

  @override
  State<MawasilatiApp> createState() => _MawasilatiAppState();
}

class _MawasilatiAppState extends State<MawasilatiApp> {
  @override
  void initState() {
    super.initState();
    _restoreSession();
  }

  Future<void> _restoreSession() async {
    final auth = context.read<AuthProvider>();
    final token = await auth.restoreToken();
    if (token == null) return;
    try {
      final me = await const ApiService().withToken(token).me();
      auth.setUser(me);
    } catch (_) {
      // Token expired or invalid — sign out silently and let the user log in again.
      await auth.signOut();
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mawasilati',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      initialRoute: '/',
      routes: {
        '/': (_) => const HomeScreen(),
        '/login': (_) => const LoginScreen(),
        '/register': (_) => const RegisterScreen(),
        '/plan-trip': (_) => const PlanTripScreen(),
        '/trip-options': (_) => const TripOptionsScreen(),
        '/trip-tracking': (_) => const TripTrackingScreen(),
        '/trip-history': (_) => const TripHistoryScreen(),
        '/chat': (_) => const ChatScreen(),
        '/payment': (_) => const PaymentScreen(),
        '/wallet': (_) => const WalletScreen(),
        '/driver-home': (_) => const DriverHomeScreen(),
        '/heatmap': (_) => const HeatmapScreen(),
        '/profile': (_) => const ProfileScreen(),
        '/settings': (_) => const SettingsScreen(),
      },
    );
  }
}
