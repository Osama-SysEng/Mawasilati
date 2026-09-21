import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/services/api_service.dart';
import '../../shared/services/session.dart';
import '../../shared/widgets/app_scaffold.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatMessage {
  _ChatMessage(this.text, {required this.fromUser});

  final String text;
  final bool fromUser;
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<_ChatMessage> _messages = [];
  bool _isSending = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    final auth = context.read<AuthProvider>();
    if (!auth.isAuthenticated) {
      Navigator.of(context).pushNamed('/login');
      return;
    }

    final text = _controller.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add(_ChatMessage(text, fromUser: true));
      _isSending = true;
    });
    _controller.clear();

    try {
      final result = await const ApiService().withToken(auth.token).chat(text);
      setState(() {
        _messages.add(_ChatMessage(result['response']?.toString() ?? '', fromUser: false));
      });
    } on ApiException catch (e) {
      setState(() {
        _messages.add(_ChatMessage('حصل خطأ: ${e.message}', fromUser: false));
      });
    } finally {
      if (mounted) {
        setState(() {
          _isSending = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'محادثة AI',
      children: [
        ..._messages.map(
          (message) => Align(
            alignment: message.fromUser ? Alignment.centerRight : Alignment.centerLeft,
            child: Card(
              color: message.fromUser ? Colors.teal.shade50 : Colors.grey.shade100,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Text(message.text),
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _controller,
          maxLines: 4,
          decoration: const InputDecoration(
            labelText: 'اكتب رحلة أو سؤال باللهجة المصرية',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: _isSending ? null : _send,
          child: Text(_isSending ? 'جاري الإرسال...' : 'إرسال'),
        ),
      ],
    );
  }
}
