abstract interface class WalletRepository {
  Future<List<Object>> load({String? cursor});
}
