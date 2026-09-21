class WalletModel {
  const WalletModel({required this.id, required this.status, this.correlationId});
  final String id;
  final String status;
  final String? correlationId;
}
