using Microsoft.EntityFrameworkCore;
using ModularWebAPI.Users.Do;
using ModularWebAPI.Users.Dto;
using ModularWebAPI.Data;
using ModularWebAPI.Shared.Enums;

namespace ModularWebAPI.Users.Services
{
    public class UsersService : IUsersService
    {
        private readonly AppDbContext _context;
        private readonly ILogger<UsersService> _logger;

        public UsersService(AppDbContext context, ILogger<UsersService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<UserResponse> GetUserByIdAsync(Guid id)
        {
            var user = await _context.Users.FindAsync(id);
            if (user == null)
                throw new KeyNotFoundException($"User with ID {id} not found");

            return MapToResponse(user);
        }

        public async Task<UserResponse> GetUserByEmailAsync(string email)
        {
            var user = await _context.Users.FirstOrDefaultAsync(u => u.Email == email);
            if (user == null)
                throw new KeyNotFoundException($"User with email {email} not found");

            return MapToResponse(user);
        }

        public async Task<(List<UserResponse> Users, int Total)> GetUsersAsync(
            int skip = 0, 
            int limit = 10, 
            string? search = null, 
            string? role = null, 
            bool? active = null)
        {
            var query = _context.Users.AsQueryable();

            // Apply filters
            if (!string.IsNullOrEmpty(search))
            {
                query = query.Where(u => 
                    u.Nom.Contains(search) || 
                    u.Prenom.Contains(search) || 
                    u.Email.Contains(search));
            }

            if (!string.IsNullOrEmpty(role) && Enum.TryParse<UserRole>(role, true, out var userRole))
            {
                query = query.Where(u => u.Role == userRole);
            }

            if (active.HasValue)
            {
                query = query.Where(u => u.Active == active.Value);
            }

            var total = await query.CountAsync();
            var users = await query
                .OrderBy(u => u.CreatedAt)
                .Skip(skip)
                .Take(limit)
                .ToListAsync();

            return (users.Select(MapToResponse).ToList(), total);
        }

        public async Task<UserResponse> CreateUserAsync(UserRequest request)
        {
            // Check if user already exists
            var existingUser = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == request.Email);

            if (existingUser != null)
            {
                throw new InvalidOperationException("User already exists");
            }

            // Create user with default password
            var user = new User
            {
                Id = Guid.NewGuid(),
                Email = request.Email,
                Nom = request.Nom,
                Prenom = request.Prenom,
                Role = request.Role,
                Active = request.Active,
                HashedPassword = BCrypt.Net.BCrypt.HashPassword("TempPassword123!"),
                CreatedAt = DateTime.UtcNow
            };

            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            return MapToResponse(user);
        }

        public async Task<UserResponse> UpdateUserAsync(Guid id, UserRequest request)
        {
            var user = await _context.Users.FindAsync(id);
            if (user == null)
                throw new KeyNotFoundException($"User with ID {id} not found");

            // Check if email is unique (if changed)
            if (user.Email != request.Email)
            {
                var existingUser = await _context.Users
                    .FirstOrDefaultAsync(u => u.Email == request.Email && u.Id != id);

                if (existingUser != null)
                {
                    throw new InvalidOperationException("Email already in use");
                }
            }

            user.Email = request.Email;
            user.Nom = request.Nom;
            user.Prenom = request.Prenom;
            user.Role = request.Role;
            user.Active = request.Active;

            await _context.SaveChangesAsync();

            return MapToResponse(user);
        }

        public async Task<bool> DeleteUserAsync(Guid id)
        {
            var user = await _context.Users.FindAsync(id);
            if (user == null)
                return false;

            _context.Users.Remove(user);
            await _context.SaveChangesAsync();

            return true;
        }

        public async Task<bool> ResetPasswordAsync(Guid id, string newPassword)
        {
            var user = await _context.Users.FindAsync(id);
            if (user == null)
                return false;

            user.HashedPassword = BCrypt.Net.BCrypt.HashPassword(newPassword);
            await _context.SaveChangesAsync();

            return true;
        }

        private static UserResponse MapToResponse(User user)
        {
            return new UserResponse
            {
                Id = user.Id,
                Email = user.Email,
                Nom = user.Nom,
                Prenom = user.Prenom,
                Role = user.Role,
                Active = user.Active,
                CreatedAt = user.CreatedAt,
                LastLogin = user.LastLogin
            };
        }
    }
}