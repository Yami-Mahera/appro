using ModularWebAPI.Auth.Dto;

namespace ModularWebAPI.Auth.Services
{
    public interface IAuthService
    {
        Task<AuthResponse> LoginAsync(LoginRequest request);
        Task<AuthResponse> RegisterAsync(RegisterRequest request);
        Task<bool> ValidateTokenAsync(string token);
        string GenerateToken(Guid userId, string email, string role);
    }
}