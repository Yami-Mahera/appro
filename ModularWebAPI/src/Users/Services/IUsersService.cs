using ModularWebAPI.Users.Dto;

namespace ModularWebAPI.Users.Services
{
    public interface IUsersService
    {
        Task<UserResponse> GetUserByIdAsync(Guid id);
        Task<UserResponse> GetUserByEmailAsync(string email);
        Task<(List<UserResponse> Users, int Total)> GetUsersAsync(int skip = 0, int limit = 10, string? search = null, string? role = null, bool? active = null);
        Task<UserResponse> CreateUserAsync(UserRequest request);
        Task<UserResponse> UpdateUserAsync(Guid id, UserRequest request);
        Task<bool> DeleteUserAsync(Guid id);
        Task<bool> ResetPasswordAsync(Guid id, string newPassword);
    }
}