import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/services/api_service.dart';
import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  String _role = 'passenger';
  bool _obscurePassword = true;
  bool _isLoading = false;
  String? _error;

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_passwordController.text.length < 6) {
      setState(() {
        _error = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final result = await const ApiService().register(
        name: _nameController.text.trim(),
        phone: _phoneController.text.trim(),
        password: _passwordController.text,
        role: _role,
      );
      if (!mounted) return;
      await context.read<AuthProvider>().signIn(
            user: Map<String, dynamic>.from(result['user'] as Map),
            token: result['access_token'].toString(),
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('تم إنشاء الحساب بنجاح')),
      );
      Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);
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
      title: 'إنشاء حساب',
      children: [
        TextField(
          controller: _nameController,
          decoration: const InputDecoration(labelText: 'الاسم'),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _phoneController,
          keyboardType: TextInputType.phone,
          decoration: const InputDecoration(labelText: 'رقم الهاتف'),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _passwordController,
          obscureText: _obscurePassword,
          decoration: InputDecoration(
            labelText: 'كلمة المرور',
            suffixIcon: IconButton(
              icon: Icon(_obscurePassword ? Icons.visibility_off : Icons.visibility),
              onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
            ),
          ),
        ),
        const SizedBox(height: 12),
        DropdownButtonFormField<String>(
          value: _role,
          decoration: const InputDecoration(labelText: 'الدور'),
          items: const [
            DropdownMenuItem(value: 'passenger', child: Text('راكب')),
            DropdownMenuItem(value: 'driver', child: Text('سائق')),
            DropdownMenuItem(value: 'admin', child: Text('إدارة')),
          ],
          onChanged: _isLoading
              ? null
              : (value) {
                  if (value != null) {
                    setState(() {
                      _role = value;
                    });
                  }
                },
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
            child: Text(_isLoading ? 'جاري التسجيل...' : 'تسجيل'),
          ),
        ),
      ],
    );
  }
}
