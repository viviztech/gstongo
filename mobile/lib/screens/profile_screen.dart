import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _isEditing = false;
  final _formKey = GlobalKey<FormState>();

  // Controllers
  late TextEditingController _nameController;
  late TextEditingController _emailController;
  late TextEditingController _phoneController;
  late TextEditingController _gstController;
  late TextEditingController _orgController;

  @override
  void initState() {
    super.initState();
    // Default values (mock)
    _nameController = TextEditingController(text: 'Ganesh Thangavel');
    _emailController = TextEditingController(text: 'ganesh@example.com');
    _phoneController = TextEditingController(text: '+91 98765 43210');
    _gstController = TextEditingController(text: '27ABCDE1234F1Z5');
    _orgController = TextEditingController(text: 'Viviz Technologies');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _gstController.dispose();
    _orgController.dispose();
    super.dispose();
  }

  void _toggleEdit() {
    setState(() {
      _isEditing = !_isEditing;
    });
  }

  void _saveProfile() {
    if (_formKey.currentState!.validate()) {
      // API call to save profile
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profile updated successfully')),
      );
      setState(() {
        _isEditing = false;
      });
    }
  }

  void _handleLogout() {
    // Clear tokens, etc.
    context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(_isEditing ? Icons.check : Icons.edit),
            onPressed: _isEditing ? _saveProfile : _toggleEdit,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              // Avatar
              Center(
                child: Stack(
                  children: [
                    CircleAvatar(
                      radius: 50,
                      backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
                      child: Text(
                        _nameController.text.isNotEmpty
                            ? _nameController.text[0].toUpperCase()
                            : 'G',
                        style: TextStyle(
                            fontSize: 40,
                            color: Theme.of(context).primaryColor,
                            fontWeight: FontWeight.bold),
                      ),
                    ),
                    if (_isEditing)
                      Positioned(
                        bottom: 0,
                        right: 0,
                        child: CircleAvatar(
                          radius: 18,
                          backgroundColor: Theme.of(context).primaryColor,
                          child: const Icon(Icons.camera_alt,
                              size: 18, color: Colors.white),
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Personal Info Section
              _buildSectionHeader('Personal Information'),
              _buildTextField(
                controller: _nameController,
                label: 'Full Name',
                icon: Icons.person,
                enabled: _isEditing,
              ),
              const SizedBox(height: 16),
              _buildTextField(
                controller: _emailController,
                label: 'Email',
                icon: Icons.email,
                enabled: false, // Email usually not editable
              ),
              const SizedBox(height: 16),
              _buildTextField(
                controller: _phoneController,
                label: 'Phone Number',
                icon: Icons.phone,
                enabled: _isEditing,
              ),
              const SizedBox(height: 24),

              // Business Info Section
              _buildSectionHeader('Business Details'),
              _buildTextField(
                controller: _orgController,
                label: 'Organization Name',
                icon: Icons.business,
                enabled: _isEditing,
              ),
              const SizedBox(height: 16),
              _buildTextField(
                controller: _gstController,
                label: 'GST Number',
                icon: Icons.verified_user,
                enabled: _isEditing,
              ),
              const SizedBox(height: 24),

              // Account Settings
              if (!_isEditing) ...[
                _buildSectionHeader('Account Settings'),
                _buildSettingsTile(
                  icon: Icons.lock_outline,
                  title: 'Change Password',
                  onTap: () {
                    // Navigate to change password screen or show dialog
                    ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Change Password Feature')));
                  },
                ),
                _buildSettingsTile(
                  icon: Icons.notifications_outlined,
                  title: 'Notifications',
                  onTap: () {},
                ),
                _buildSettingsTile(
                  icon: Icons.language,
                  title: 'Language',
                  onTap: () {},
                ),
                 _buildSettingsTile(
                  icon: Icons.security,
                  title: 'Privacy & Security',
                  onTap: () {},
                ),
                 _buildSettingsTile(
                  icon: Icons.help_outline,
                  title: 'Help & Support',
                  onTap: () {},
                ),
                const SizedBox(height: 20),
                
                // Logout Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _handleLogout,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red[50], // Light red background
                      foregroundColor: Colors.red, // Red text
                      elevation: 0,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                        side: BorderSide(color: Colors.red.withOpacity(0.5)),
                      ),
                    ),
                    child: const Text('Log Out'),
                  ),
                ),
                const SizedBox(height: 40),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.only(bottom: 16),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: Colors.grey[800],
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool enabled = true,
  }) {
    return TextFormField(
      controller: controller,
      enabled: enabled,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, color: enabled ? Theme.of(context).primaryColor : Colors.grey),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        filled: !enabled,
        fillColor: enabled ? null : Colors.grey[100],
      ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter $label';
        }
        return null;
      },
    );
  }

  Widget _buildSettingsTile({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: Theme.of(context).primaryColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: Theme.of(context).primaryColor, size: 20),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey),
      onTap: onTap,
    );
  }
}
