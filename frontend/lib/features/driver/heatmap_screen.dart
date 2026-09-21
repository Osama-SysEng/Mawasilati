import 'package:flutter/material.dart';

import '../../shared/services/api_service.dart';
import '../../shared/widgets/app_scaffold.dart';

class HeatmapScreen extends StatefulWidget {
  const HeatmapScreen({super.key});

  @override
  State<HeatmapScreen> createState() => _HeatmapScreenState();
}

class _HeatmapScreenState extends State<HeatmapScreen> {
  late final Future<Map<String, dynamic>> _heatmapFuture;

  @override
  void initState() {
    super.initState();
    _heatmapFuture = const ApiService().getHeatmap();
  }

  Color _colorFor(String? name) {
    switch (name) {
      case 'red':
        return Colors.red;
      case 'yellow':
        return Colors.amber;
      default:
        return Colors.green;
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'خريطة كثافة السائقين',
      children: [
        FutureBuilder<Map<String, dynamic>>(
          future: _heatmapFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: Center(child: CircularProgressIndicator()),
              );
            }
            if (snapshot.hasError) {
              return Text('تعذر تحميل الخريطة: ${snapshot.error}', style: const TextStyle(color: Colors.red));
            }
            final cells = (snapshot.data?['cells'] as List?) ?? [];
            return Column(
              children: cells.map((raw) {
                final cell = Map<String, dynamic>.from(raw as Map);
                return ListTile(
                  leading: CircleAvatar(backgroundColor: _colorFor(cell['color']?.toString())),
                  title: Text('${cell['latitude']}, ${cell['longitude']}'),
                  subtitle: Text('الطلب: ${cell['demand_level']}'),
                );
              }).toList(),
            );
          },
        ),
      ],
    );
  }
}
