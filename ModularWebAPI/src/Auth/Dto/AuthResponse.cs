using ModularWebAPI.Users.Dto;

namespace ModularWebAPI.Auth.Dto
{
    public class AuthResponse
    {
        public string AccessToken { get; set; } = string.Empty;
        public string TokenType { get; set; } = "Bearer";
        public UserResponse User { get; set; } = null!;
    }
}