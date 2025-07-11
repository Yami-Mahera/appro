using System.ComponentModel.DataAnnotations;
using ModularWebAPI.Shared.Enums;

namespace ModularWebAPI.Users.Dto
{
    public class UserRequest
    {
        [Required]
        [EmailAddress]
        public string Email { get; set; } = string.Empty;
        
        [Required]
        [StringLength(100)]
        public string Nom { get; set; } = string.Empty;
        
        [Required]
        [StringLength(100)]
        public string Prenom { get; set; } = string.Empty;
        
        public UserRole Role { get; set; } = UserRole.Utilisateur;
        
        public bool Active { get; set; } = true;
    }
}