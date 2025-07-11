using System.ComponentModel.DataAnnotations;
using ModularWebAPI.Shared.Enums;

namespace ModularWebAPI.Auth.Do
{
    public class Alerte
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();
        
        [Required]
        public AlerteType Type { get; set; }
        
        [Required]
        public AlertePriorite Priorite { get; set; }
        
        [Required]
        [StringLength(200)]
        public string Titre { get; set; } = string.Empty;
        
        [Required]
        [StringLength(1000)]
        public string Message { get; set; } = string.Empty;
        
        public Guid? ArticleId { get; set; }
        
        public Guid? CommandeId { get; set; }
        
        public Guid? FournisseurId { get; set; }
        
        public bool Lue { get; set; } = false;
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}