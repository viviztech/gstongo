import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

import 'config/theme.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/filings_screen.dart';
import 'screens/filing_detail_screen.dart';
import 'screens/invoices_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/itr_filings_screen.dart';
import 'screens/tds_filings_screen.dart';
import 'screens/services_screen.dart';
import 'screens/vault_screen.dart';
import 'screens/support_screen.dart';
import 'screens/analytics_screen.dart';

final FlutterLocalNotificationsPlugin _notificationsPlugin =
    FlutterLocalNotificationsPlugin();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize notifications
  const AndroidInitializationSettings androidSettings =
      AndroidInitializationSettings('@mipmap/ic_launcher');
  const InitializationSettings settings =
      InitializationSettings(android: androidSettings);
  await _notificationsPlugin.initialize(settings);
  
  runApp(
    const ProviderScope(
      child: GSTONGOApp(),
    ),
  );
}

class GSTONGOApp extends ConsumerWidget {
  const GSTONGOApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'GSTONGO',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.light,
      routerConfig: _router,
      debugShowCheckedModeBanner: false,
    );
  }
}

final GoRouter _router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      name: 'splash',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/login',
      name: 'login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/register',
      name: 'register',
      builder: (context, state) => const RegisterScreen(),
    ),
    GoRoute(
      path: '/dashboard',
      name: 'dashboard',
      builder: (context, state) => const DashboardScreen(),
    ),
    // GST Filings
    GoRoute(
      path: '/filings',
      name: 'filings',
      builder: (context, state) => const FilingsScreen(),
    ),
    GoRoute(
      path: '/filings/:id',
      name: 'filing-detail',
      builder: (context, state) => FilingDetailScreen(id: state.pathParameters['id']!),
    ),
    // ITR Filings
    GoRoute(
      path: '/itr',
      name: 'itr',
      builder: (context, state) => const ItrFilingsScreen(),
    ),
    // TDS Filings
    GoRoute(
      path: '/tds',
      name: 'tds',
      builder: (context, state) => const TdsFilingsScreen(),
    ),
    // Business Services
    GoRoute(
      path: '/services',
      name: 'services',
      builder: (context, state) => const ServicesScreen(),
    ),
    // Document Vault
    GoRoute(
      path: '/vault',
      name: 'vault',
      builder: (context, state) => const VaultScreen(),
    ),
    // Invoices
    GoRoute(
      path: '/invoices',
      name: 'invoices',
      builder: (context, state) => const InvoicesScreen(),
    ),
    // Support
    GoRoute(
      path: '/support',
      name: 'support',
      builder: (context, state) => const SupportScreen(),
    ),
    // Analytics
    GoRoute(
      path: '/analytics',
      name: 'analytics',
      builder: (context, state) => const AnalyticsScreen(),
    ),
    // Profile
    GoRoute(
      path: '/profile',
      name: 'profile',
      builder: (context, state) => const ProfileScreen(),
    ),
  ],
);
