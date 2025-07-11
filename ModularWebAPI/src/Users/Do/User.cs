using System.ComponentModel.DataAnnotations;
using ModularWebAPI.Shared.Enums;

namespace ModularWebAPI.Users.Do
{
    public class User
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();
        
        [Required]
        [EmailAddress]
        [StringLength(255)]
        public string Email { get; set; } = string.Empty;
        
        [Required]
        [StringLength(100)]
        public string Nom { get; set; } = string.Empty;
        
        [Required]
        [StringLength(100)]
        public string Prenom { get; set; } = string.Empty;
        
        [Required]
        public UserRole Role { get; set; } = UserRole.Utilisateur;
        
        [Required]
        public string HashedPassword { get; set; } = string.Empty;
        
        public bool Active { get; set; } = true;
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime? LastLogin { get; set; }
    }
}