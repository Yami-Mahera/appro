using System.ComponentModel.DataAnnotations;

namespace ModularWebAPI.Auth.Do
{
    public class Fournisseur
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();
        
        [Required]
        [StringLength(200)]
        public string Nom { get; set; } = string.Empty;
        
        [Required]
        [StringLength(50)]
        public string CodeFournisseur { get; set; } = string.Empty;
        
        [Required]
        [StringLength(500)]
        public string Adresse { get; set; } = string.Empty;
        
        [Required]
        [StringLength(100)]
        public string Ville { get; set; } = string.Empty;
        
        [Required]
        [StringLength(20)]
        public string CodePostal { get; set; } = string.Empty;
        
        [Required]
        [StringLength(100)]
        public string Pays { get; set; } = string.Empty;
        
        [StringLength(20)]
        public string? Telephone { get; set; }
        
        [EmailAddress]
        [StringLength(255)]
        public string? Email { get; set; }
        
        [StringLength(255)]
        public string? SiteWeb { get; set; }
        
        [StringLength(200)]
        public string? ConditionsPaiement { get; set; }
        
        public int? DelaiLivraisonMoyen { get; set; }
        
        public bool Active { get; set; } = true;
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
        
        public ICollection<Contact> Contacts { get; set; } = new List<Contact>();
    }
}